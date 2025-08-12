# services/chatbot_service.py
import re
import json
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime, date, timedelta
from decimal import Decimal
from sqlalchemy.orm import Session
from uuid import UUID
import asyncio
from openai import OpenAI

from schemas.chat_schema import Intent, ActionType, TransactionFromChatRequest
from schemas.transaction_schema import TransactionCreate
from crud import transaction_crud
from crud.category_crud import get_user_category_id_by_display_name
from app.config import settings  # Import your settings

class FinancialChatbotService:
    """Financial advice chatbot service with NLP capabilities"""
    
    def __init__(self):
        # Initialize OpenAI client with OpenRouter
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=settings.OPENAI_API_KEY  # Use your config
        )
        
        self.intent_patterns = {
            Intent.ADD_TRANSACTION: [
                r"(add|create|record|log|enter)\s+(transaction|expense|income|spending|purchase)",
                r"(spent|bought|purchased|paid|received|earned)\s+.*(\d+)",
                r"(tôi|mình)\s+(đã|vừa)?\s*(chi|tiêu|mua|nhận|kiếm)\s+.*(\d+)",
                r"(record|ghi lại|ghi nhận)\s+.*(\d+)",
            ],
            Intent.GET_BALANCE: [
                r"(what|how much|show|tell)\s+(is|me)?\s*(my)?\s*(balance|money|cash|total)",
                r"(số dư|tổng tiền|tình hình tài chính|balance)",
                r"(tôi|mình)\s+có\s+(bao nhiêu|tổng cộng)",
            ],
            Intent.GET_SPENDING: [
                r"(how much|what)\s+(did|have)?\s*(i|we)?\s*(spend|spent|spending)",
                r"(show|tell)\s+.*spending",
                r"(chi tiêu|tiêu|expenses|spending)",
                r"(tôi|mình)\s+(đã|vừa)?\s*(chi|tiêu)\s+bao nhiêu",
            ],
            Intent.BUDGET_ADVICE: [
                r"(advice|suggest|recommend|help).*budget",
                r"(how to|should i).*save",
                r"(financial|money)\s+(advice|tip|help)",
                r"(lời khuyên|tư vấn|hướng dẫn).*((tài chính|tiết kiệm|ngân sách))",
            ],
            Intent.GREETING: [
                r"^(hi|hello|hey|good morning|good afternoon|good evening|xin chào|chào|hello)",
                r"^(start|begin|bắt đầu)",
            ],
            Intent.GOODBYE: [
                r"(bye|goodbye|see you|thanks|thank you|cảm ơn|tạm biệt|chào|kết thúc)",
                r"(that's all|done|finish|xong|hết|thế thôi)",
            ],
        }
        
        self.entity_patterns = {
            'amount': [
                r'(\d{1,3}(?:[,\.]\d{3})*(?:[,\.]\d{2})?)',  # Numbers with separators
                r'(\d+(?:\.\d{2})?)',  # Simple decimals
                r'(\d+)\s*(k|thousand|nghìn|ngàn)',  # Thousands
                r'(\d+)\s*(m|million|triệu)',  # Millions
            ],
            'transaction_type': [
                r'(income|earn|received|salary|bonus|thu nhập|lương|nhận)',
                r'(expense|spent|buy|purchase|paid|chi|tiêu|mua|trả)',
            ],
            'category': [
                r'(food|restaurant|groceries|ăn uống|thức ăn|nhà hàng)',
                r'(transport|travel|taxi|bus|di chuyển|đi lại)',
                r'(entertainment|movie|game|giải trí|phim|game)',
                r'(shopping|clothes|mua sắm|quần áo)',
                r'(health|medical|y tế|sức khỏe)',
                r'(education|học tập|giáo dục)',
            ],
            'date': [
                r'(today|hôm nay)',
                r'(yesterday|hôm qua)',
                r'(last week|tuần trước)',
                r'(\d{1,2}[/-]\d{1,2}[/-]\d{4})',
                r'(\d{1,2}[/-]\d{1,2})',
            ],
        }

    def detect_intent(self, message: str) -> Tuple[Optional[Intent], float]:
        """Detect intent from user message"""
        message = message.lower().strip()
        
        # Check patterns for each intent
        for intent, patterns in self.intent_patterns.items():
            for pattern in patterns:
                if re.search(pattern, message, re.IGNORECASE):
                    confidence = 0.8  # Base confidence
                    if len([p for p in patterns if re.search(p, message, re.IGNORECASE)]) > 1:
                        confidence = 0.9  # Higher confidence if multiple patterns match
                    return intent, confidence
        
        return Intent.GENERAL_QUERY, 0.5

    def extract_entities(self, message: str, intent: Intent) -> Dict[str, Any]:
        """Extract entities from message based on intent"""
        entities = {}
        message_lower = message.lower().strip()
        
        # Extract amount
        for pattern in self.entity_patterns['amount']:
            match = re.search(pattern, message_lower, re.IGNORECASE)
            if match:
                amount_str = match.group(1)
                # Handle thousand/million suffixes
                if any(suffix in message_lower for suffix in ['k', 'thousand', 'nghìn', 'ngàn']):
                    amount_str = str(float(amount_str.replace(',', '').replace('.', '')) * 1000)
                elif any(suffix in message_lower for suffix in ['m', 'million', 'triệu']):
                    amount_str = str(float(amount_str.replace(',', '').replace('.', '')) * 1000000)
                
                # Clean amount string
                amount_str = amount_str.replace(',', '')
                try:
                    entities['amount'] = float(amount_str)
                except ValueError:
                    entities['amount'] = None
                break
        
        # Extract transaction type for ADD_TRANSACTION intent
        if intent == Intent.ADD_TRANSACTION:
            for pattern in self.entity_patterns['transaction_type']:
                match = re.search(pattern, message_lower, re.IGNORECASE)
                if match:
                    if any(word in match.group(0).lower() for word in ['income', 'earn', 'received', 'salary', 'thu nhập', 'lương', 'nhận']):
                        entities['transaction_type'] = 'income'
                    else:
                        entities['transaction_type'] = 'expense'
                    break
            
            # Default to expense if not specified
            if 'transaction_type' not in entities:
                entities['transaction_type'] = 'expense'
        
        # Extract category
        for pattern in self.entity_patterns['category']:
            match = re.search(pattern, message_lower, re.IGNORECASE)
            if match:
                category_text = match.group(0).lower()
                if any(word in category_text for word in ['food', 'restaurant', 'ăn uống', 'thức ăn', 'nhà hàng']):
                    entities['category'] = 'Ăn uống'
                elif any(word in category_text for word in ['transport', 'travel', 'di chuyển', 'đi lại']):
                    entities['category'] = 'Di chuyển'
                elif any(word in category_text for word in ['entertainment', 'giải trí']):
                    entities['category'] = 'Giải trí'
                elif any(word in category_text for word in ['shopping', 'mua sắm']):
                    entities['category'] = 'Mua sắm'
                elif any(word in category_text for word in ['health', 'y tế']):
                    entities['category'] = 'Y tế'
                elif any(word in category_text for word in ['education', 'học tập']):
                    entities['category'] = 'Giáo dục'
                break
        
        # Extract date
        for pattern in self.entity_patterns['date']:
            match = re.search(pattern, message_lower, re.IGNORECASE)
            if match:
                date_text = match.group(0).lower()
                if 'today' in date_text or 'hôm nay' in date_text:
                    entities['date'] = datetime.now().date().isoformat()
                elif 'yesterday' in date_text or 'hôm qua' in date_text:
                    entities['date'] = (datetime.now().date() - timedelta(days=1)).isoformat()
                # Add more date parsing logic as needed
                break
        
        return entities

    async def generate_ai_response(
        self, 
        user_message: str, 
        intent: Intent, 
        entities: Dict[str, Any],
        financial_context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Generate AI response using OpenRouter/OpenAI"""
        try:
            # Build system prompt based on intent and context
            system_prompt = self._build_system_prompt(intent, financial_context)
            
            # Build user context
            user_context = f"User message: {user_message}\n"
            if entities:
                user_context += f"Extracted entities: {json.dumps(entities, ensure_ascii=False)}\n"
            if financial_context:
                user_context += f"Financial context: {json.dumps(financial_context, ensure_ascii=False)}\n"
            
            completion = self.client.chat.completions.create(
                model="openai/gpt-3.5-turbo",  # or use "openai/gpt-4" for better results
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_context}
                ],
                max_tokens=500,
                temperature=0.7
            )
            
            return completion.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"AI response generation error: {str(e)}")
            return self._get_fallback_response(intent)

    def _build_system_prompt(self, intent: Intent, financial_context: Optional[Dict[str, Any]] = None) -> str:
        """Build system prompt based on intent and context"""
        base_prompt = """Bạn là một trợ lý tài chính thông minh và thân thiện, chuyên giúp người dùng quản lý tài chính cá nhân. 
Bạn có thể trả lời bằng tiếng Việt và tiếng Anh tùy theo ngôn ngữ của người dùng.
Hãy đưa ra lời khuyên thực tế, dễ hiểu và có thể áp dụng được."""
        
        if intent == Intent.BUDGET_ADVICE:
            return f"""{base_prompt}
            
Nhiệm vụ: Đưa ra lời khuyên tài chính dựa trên tình hình tài chính của người dùng.
Quy tắc:
- Phân tích tình hình tài chính hiện tại
- Đưa ra lời khuyên cụ thể và thực tế
- Sử dụng emoji phù hợp để làm sinh động
- Đề xuất các bước hành động cụ thể
- Khuyến khích thói quen tài chính tốt"""

        elif intent == Intent.GENERAL_QUERY:
            return f"""{base_prompt}
            
Nhiệm vụ: Trả lời các câu hỏi tài chính tổng quát.
Quy tắc:
- Cung cấp thông tin chính xác và hữu ích
- Giải thích các khái niệm tài chính một cách đơn giản
- Đưa ra ví dụ thực tế khi cần thiết
- Khuyến khích người dùng học hỏi thêm về tài chính"""

        else:
            return f"""{base_prompt}
            
Nhiệm vụ: Hỗ trợ người dùng với các tác vụ quản lý tài chính.
Hãy trả lời một cách thân thiện và hữu ích."""

    def _get_fallback_response(self, intent: Intent) -> str:
        """Get fallback response when AI fails"""
        fallback_responses = {
            Intent.BUDGET_ADVICE: "💡 Tôi khuyên bạn nên theo dõi chi tiêu hàng ngày, lập ngân sách tháng và tiết kiệm ít nhất 20% thu nhập. Bạn có muốn tôi phân tích chi tiết hơn không?",
            Intent.GENERAL_QUERY: "Tôi có thể giúp bạn với nhiều vấn đề tài chính. Hãy hỏi tôi về giao dịch, số dư, chi tiêu hoặc lời khuyên tài chính nhé!",
            Intent.GREETING: "Xin chào! Tôi là trợ lý tài chính của bạn. Tôi có thể giúp bạn quản lý thu chi, đưa ra lời khuyên và phân tích tài chính. Bạn cần hỗ trợ gì?",
            Intent.GOODBYE: "Cảm ơn bạn đã sử dụng dịch vụ! Hãy tiếp tục quản lý tài chính thông minh nhé! 👋"
        }
        return fallback_responses.get(intent, "Xin lỗi, tôi không hiểu yêu cầu của bạn. Vui lòng thử lại!")

    async def generate_response(
        self, 
        intent: Intent, 
        entities: Dict[str, Any], 
        user_id: UUID,
        user_message: str,
        db: Session
    ) -> Tuple[str, Optional[ActionType], Optional[Dict[str, Any]]]:
        """Generate bot response based on intent and entities"""
        
        if intent == Intent.GREETING:
            return self._handle_greeting(), ActionType.NO_ACTION, None
            
        elif intent == Intent.GOODBYE:
            return self._handle_goodbye(), ActionType.NO_ACTION, None
            
        elif intent == Intent.ADD_TRANSACTION:
            return await self._handle_add_transaction(entities, user_id, db)
            
        elif intent == Intent.GET_BALANCE:
            return await self._handle_get_balance(user_id, db)
            
        elif intent == Intent.GET_SPENDING:
            return await self._handle_get_spending(entities, user_id, db)
            
        elif intent == Intent.BUDGET_ADVICE:
            return await self._handle_budget_advice(user_message, user_id, db)
            
        else:  # GENERAL_QUERY
            return await self._handle_general_query(user_message, entities)

    def _handle_greeting(self) -> str:
        """Handle greeting messages"""
        return """Xin chào! Tôi là trợ lý tài chính cá nhân của bạn. 🤖💰

Tôi có thể giúp bạn:
• Ghi nhận giao dịch thu chi
• Kiểm tra số dư và tình hình tài chính
• Đưa ra lời khuyên về ngân sách và tiết kiệm
• Phân tích chi tiêu của bạn

Bạn muốn làm gì hôm nay?"""

    def _handle_goodbye(self) -> str:
        """Handle goodbye messages"""
        return "Cảm ơn bạn đã sử dụng dịch vụ! Chúc bạn quản lý tài chính hiệu quả! 👋💰"

    async def _handle_add_transaction(
        self, 
        entities: Dict[str, Any], 
        user_id: UUID, 
        db: Session
    ) -> Tuple[str, ActionType, Optional[Dict[str, Any]]]:
        """Handle transaction creation"""
        
        # Check if we have required information
        missing_info = []
        if 'amount' not in entities or entities['amount'] is None:
            missing_info.append("số tiền")
        if 'category' not in entities:
            missing_info.append("danh mục")
        
        if missing_info:
            return (
                f"Để ghi nhận giao dịch, tôi cần thêm thông tin về: {', '.join(missing_info)}. "
                f"Ví dụ: 'Tôi vừa chi 50000 đồng mua thức ăn'",
                ActionType.NO_ACTION,
                None
            )
        
        try:
            # Create transaction
            transaction_data = TransactionCreate(
                transaction_type=entities.get('transaction_type', 'expense'),
                amount=Decimal(str(entities['amount'])),
                description=f"Giao dịch tạo từ chatbot",
                category_display_name=entities['category'],
                transaction_date=datetime.now().date(),
                payment_method="Khác",
                created_by="chatbot"
            )
            
            created_transaction = transaction_crud.create_transaction(
                db=db,
                user_id=user_id,
                transaction_data=transaction_data
            )
            
            transaction_type_vn = "thu nhập" if entities.get('transaction_type') == 'income' else "chi tiêu"
            
            return (
                f"✅ Đã ghi nhận giao dịch thành công!\n\n"
                f"📋 Chi tiết:\n"
                f"• Loại: {transaction_type_vn.title()}\n"
                f"• Số tiền: {entities['amount']:,.0f} VNĐ\n"
                f"• Danh mục: {entities['category']}\n"
                f"• Thời gian: {datetime.now().strftime('%d/%m/%Y %H:%M')}",
                ActionType.TRANSACTION_CREATED,
                {
                    "transaction_id": str(created_transaction.TransactionID),
                    "amount": entities['amount'],
                    "category": entities['category'],
                    "type": entities.get('transaction_type', 'expense')
                }
            )
            
        except Exception as e:
            return (
                f"❌ Có lỗi xảy ra khi ghi nhận giao dịch: {str(e)}\n"
                f"Vui lòng thử lại hoặc kiểm tra thông tin danh mục.",
                ActionType.NO_ACTION,
                None
            )

    async def _handle_get_balance(
        self, 
        user_id: UUID, 
        db: Session
    ) -> Tuple[str, ActionType, Optional[Dict[str, Any]]]:
        """Handle balance inquiry"""
        try:
            summary = transaction_crud.get_transaction_summary(db=db, user_id=user_id)
            
            return (
                f"💰 **Tình hình tài chính của bạn:**\n\n"
                f"📈 Tổng thu nhập: {summary['total_income']:,.0f} VNĐ\n"
                f"📉 Tổng chi tiêu: {summary['total_expense']:,.0f} VNĐ\n"
                f"💵 Số dư ròng: {summary['net_amount']:,.0f} VNĐ\n\n"
                f"{'🟢 Bạn đang có thặng dư!' if summary['net_amount'] >= 0 else '🔴 Bạn đang chi tiêu nhiều hơn thu nhập!'}",
                ActionType.BALANCE_RETRIEVED,
                {
                    "total_income": float(summary['total_income']),
                    "total_expense": float(summary['total_expense']),
                    "net_amount": float(summary['net_amount'])
                }
            )
            
        except Exception as e:
            return (
                "❌ Không thể lấy thông tin số dư. Vui lòng thử lại sau.",
                ActionType.NO_ACTION,
                None
            )

    async def _handle_get_spending(
        self, 
        entities: Dict[str, Any], 
        user_id: UUID, 
        db: Session
    ) -> Tuple[str, ActionType, Optional[Dict[str, Any]]]:
        """Handle spending inquiry"""
        try:
            # Get spending for current month by default
            today = date.today()
            start_of_month = date(today.year, today.month, 1)
            
            summary = transaction_crud.get_transaction_summary(
                db=db, 
                user_id=user_id,
                date_from=start_of_month,
                date_to=today
            )
            
            return (
                f"📊 **Chi tiêu tháng {today.month}/{today.year}:**\n\n"
                f"💸 Tổng chi tiêu: {summary['total_expense']:,.0f} VNĐ\n"
                f"💰 Thu nhập: {summary['total_income']:,.0f} VNĐ\n"
                f"📈 Còn lại: {summary['net_amount']:,.0f} VNĐ\n\n"
                f"📅 Từ ngày {start_of_month.strftime('%d/%m')} đến {today.strftime('%d/%m')}",
                ActionType.NO_ACTION,
                {
                    "period": f"{today.month}/{today.year}",
                    "total_expense": float(summary['total_expense']),
                    "total_income": float(summary['total_income'])
                }
            )
            
        except Exception as e:
            return (
                "❌ Không thể lấy thông tin chi tiêu. Vui lòng thử lại sau.",
                ActionType.NO_ACTION,
                None
            )

    async def _handle_budget_advice(
        self, 
        user_message: str,
        user_id: UUID, 
        db: Session
    ) -> Tuple[str, ActionType, Optional[Dict[str, Any]]]:
        """Handle budget advice request with AI"""
        try:
            # Get financial context
            summary = transaction_crud.get_transaction_summary(db=db, user_id=user_id)
            
            financial_context = {
                "total_income": float(summary['total_income']),
                "total_expense": float(summary['total_expense']),
                "net_amount": float(summary['net_amount']),
                "expense_ratio": (float(summary['total_expense']) / float(summary['total_income']) * 100) if summary['total_income'] > 0 else 0
            }
            
            # Generate AI response
            ai_response = await self.generate_ai_response(
                user_message=user_message,
                intent=Intent.BUDGET_ADVICE,
                entities={},
                financial_context=financial_context
            )
            
            return (ai_response, ActionType.ADVICE_GIVEN, {"advice_type": "budget", "ai_generated": True})
            
        except Exception as e:
            # Fallback to rule-based advice
            return (
                self._get_fallback_response(Intent.BUDGET_ADVICE),
                ActionType.ADVICE_GIVEN,
                {"advice_type": "budget", "ai_generated": False}
            )

    async def _handle_general_query(
        self, 
        user_message: str, 
        entities: Dict[str, Any]
    ) -> Tuple[str, ActionType, Optional[Dict[str, Any]]]:
        """Handle general queries with AI"""
        try:
            ai_response = await self.generate_ai_response(
                user_message=user_message,
                intent=Intent.GENERAL_QUERY,
                entities=entities
            )
            
            return (ai_response, ActionType.NO_ACTION, {"ai_generated": True})
            
        except Exception as e:
            return (
                self._get_fallback_response(Intent.GENERAL_QUERY),
                ActionType.NO_ACTION,
                {"ai_generated": False}
            )

# Initialize service instance
chatbot_service = FinancialChatbotService()