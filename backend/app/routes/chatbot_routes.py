from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.auth.auth_dependency import get_current_user
from app import models, crud
from app.config import OPENAI_API_KEY
import aiohttp
import uuid
from datetime import datetime
from redis import Redis
import json
import logging

# Cấu hình logging để theo dõi hiệu suất
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/chatbot", tags=["Chatbot"])
redis_client = Redis(host="localhost", port=6379, db=0)

async def parse_transaction(question: str, user_id: str, db: Session):
    prompt = f"""
    Phân tích câu hỏi sau và trả về JSON với intent và entities:
    Câu hỏi: {question}
    Định dạng trả về:
    {{
      "intent": "record_transaction",
      "entities": {{"amount": float, "category": str, "date": str, "type": "expense|income"}},
      "confidence_score": float
    }}
    """
    response = await call_openai(prompt, "vi")  # Mặc định tiếng Việt
    result = response["choices"][0]["message"]["content"]
    data = json.loads(result)

    if data["intent"] == "record_transaction":
        amount = data["entities"]["amount"]
        category_name = data["entities"]["category"]
        date_str = data["entities"]["date"]
        transaction_type = data["entities"]["type"]

        # Xử lý ngày
        transaction_date = datetime.utcnow().date()
        transaction_time = datetime.utcnow().time()
        if date_str in ["yesterday", "hôm qua"]:
            transaction_date = (datetime.utcnow() - timedelta(days=1)).date()

        # Tìm danh mục
        category = db.query(models.Category).filter(models.Category.name.ilike(f"%{category_name}%")).first()
        if not category:
            category = db.query(models.Category).filter(models.Category.name == "other").first()

        # Lưu giao dịch
        transaction = models.Transaction(
            user_id=user_id,
            category_id=category.id,
            transaction_type=transaction_type,
            amount=amount,
            description=question,
            transaction_date=transaction_date,
            transaction_time=transaction_time,
            created_by="chatbot"
        )
        db.add(transaction)
        db.commit()

        # Lưu intent và entities vào chat_messages
        crud.save_chat_message(
            db, user_id, str(uuid.uuid4()), question,
            f"Đã ghi giao dịch: {amount} cho {category.name} ({'chi tiêu' if transaction_type == 'expense' else 'thu nhập'})",
            intent="record_transaction",
            entities=data["entities"],
            confidence_score=data["confidence_score"]
        )
        return f"Đã ghi giao dịch: {amount} cho {category.name} ({'chi tiêu' if transaction_type == 'expense' else 'thu nhập'})"
    return None

# # Hàm giả lập đồng bộ giao dịch MoMo (chưa phát triển)
# async def fetch_momo_transactions(access_token: str):
#     """Hàm giả lập đồng bộ giao dịch MoMo (cần thay bằng API thực tế)"""
#     async with aiohttp.ClientSession() as session:
#         async with session.get(
#             "https://api.momo.vn/transactions",  # URL giả định
#             headers={"Authorization": f"Bearer {access_token}"}
#         ) as response:
#             return await response.json()

# # Hàm đồng bộ giao dịch từ ví điện tử (chưa phát triển)
# async def sync_wallet(provider: str, access_token: str, user_id: str, db: Session, language: str):
#     """Đồng bộ giao dịch từ ví điện tử"""
#     if provider.lower() not in ["momo", "zalopay"]:
#         return "Nhà cung cấp không được hỗ trợ." if language == "vi" else "Provider not supported."
        
#     try:
#         integration = db.query(models.ExternalIntegration).filter(
#             models.ExternalIntegration.user_id == user_id,
#             models.ExternalIntegration.provider == provider
#         ).first()
#         if not integration:
#             integration = models.ExternalIntegration(
#                 user_id=user_id,
#                 provider=provider,
#                 access_token=access_token,
#                 created_at=datetime.utcnow()
#             )
#             db.add(integration)
#             db.commit()
            
#         transactions = await fetch_momo_transactions(access_token) if provider.lower() == "momo" else []
#         for tx in transactions.get("data", []):
#             category = db.query(models.Category).filter(models.Category.name.ilike(f"%{tx.get('category', 'other')}%")).first()
#             if not category:
#                 category = db.query(models.Category).filter(models.Category.name == "other").first()
                
#             transaction = models.Transaction(
#                 user_id=user_id,
#                 amount=tx["amount"],
#                 category_id=category.id,
#                 type="expense" if tx["type"] == "debit" else "income",
#                 date=datetime.fromisoformat(tx["date"]),
#                 description=tx.get("description", "")
#             )
#             db.add(transaction)
            
#         sync_log = models.SyncLog(
#             integration_id=integration.id,
#             status="success",
#             details=f"Đồng bộ {len(transactions.get('data', []))} giao dịch",
#             timestamp=datetime.utcnow()
#         )
#         db.add(sync_log)
#         db.commit()
        
#         return (
#             f"Đã đồng bộ {len(transactions.get('data', []))} giao dịch từ {provider}"
#             if language == "vi"
#             else f"Synced {len(transactions.get('data', []))} transactions from {provider}"
#         )
#     except Exception as e:
#         sync_log = models.SyncLog(
#             integration_id=integration.id,
#             status="failed",
#             details=str(e),
#             timestamp=datetime.utcnow()
#         )
#         db.add(sync_log)
#         db.commit()
#         return f"Lỗi đồng bộ: {str(e)}" if language == "vi" else f"Sync error: {str(e)}"

def get_category_spending(db: Session, user_id: str, category_name: str, month: int, year: int):
    """Truy vấn chi tiêu theo danh mục cho báo cáo"""
    category = db.query(models.Category).filter(models.Category.name.ilike(f"%{category_name}%")).first()
    if category:
        total = db.query(models.Transaction).filter(
            models.Transaction.user_id == user_id,
            models.Transaction.category_id == category.id,
            models.Transaction.type == "expense",
            models.Transaction.transaction_date.month == month,  # Sửa từ date thành transaction_date
            models.Transaction.transaction_date.year == year     # Sửa từ date thành transaction_date
        ).with_entities(func.sum(models.Transaction.amount)).scalar()
        total = total or 0
        return f"Bạn đã chi {total} cho {category.name} trong tháng {month}/{year}"
    return f"Không tìm thấy danh mục {category_name}"

def get_optimization_suggestion(summary: dict):
    """Đề xuất tối ưu chi tiêu dựa trên ngân sách"""
    for category_id, budget in summary["budgets"].items():
        if budget["spent"] > budget["limit"] * 0.8:
            return f"Bạn sắp vượt ngân sách {budget['category_name']} ({budget['spent']}/{budget['limit']}). Hãy giảm bớt chi tiêu nhé!"
    return "Chi tiêu của bạn đang ổn, cứ tiếp tục nhé!"

async def call_openai(prompt: str):
    """Gọi API OpenAI bất đồng bộ"""
    async with aiohttp.ClientSession() as session:
        async with session.post(
            "https://api.openai.com/v1/chat/completions",
            headers={"Authorization": f"Bearer {OPENAI_API_KEY}"},
            json={
                "model": "gpt-3.5-turbo",
                "messages": [
                    {
                        "role": "system",
                        "content": "Bạn là trợ lý tài chính thân thiện, châm biếm nhẹ, trả lời bằng tiếng Việt."
                    },
                    {"role": "user", "content": prompt}
                ]
            }
        ) as response:
            return await response.json()

@router.post("/ask")
async def ask_chatbot(question: str, db: Session = Depends(), current_user: models.User = Depends(get_current_user)):
    start_time = time.time()  # Đo thời gian phản hồi
    
    try:
        # Lấy tóm tắt từ cache hoặc DB
        cached_summary = redis_client.get(f"summary:{current_user.id}")
        if cached_summary:
            summary = json.loads(cached_summary)
        else:
            summary = crud.get_user_summary(db, current_user.id)
            redis_client.setex(f"summary:{current_user.id}", 3600, json.dumps(summary))

        # # Xử lý yêu cầu đồng bộ ví (chưa phát triển)
        # if "đồng bộ" in question.lower() or "sync" in question.lower():
        #     provider = "momo" if "momo" in question.lower() else "zalopay"
        #     # Giả định access_token được lưu trong external_integrations
        #     integration = db.query(models.ExternalIntegration).filter(
        #         models.ExternalIntegration.user_id == current_user.id,
        #         models.ExternalIntegration.provider == provider
        #     ).first()
        #     if integration:
        #         sync_response = await sync_wallet(provider, integration.access_token, current_user.id, db, "vi")
        #         crud.save_chat_message(db, current_user.id, str(uuid.uuid4()), question, sync_response)
        #         logger.info(f"Chatbot response time: {time.time() - start_time} seconds")
        #         return {"answer": sync_response}
        #     else:
        #         response = f"Bạn chưa kết nối ví {provider}. Hãy kết nối trước!"
        #         crud.save_chat_message(db, current_user.id, str(uuid.uuid4()), question, response)
        #         logger.info(f"Chatbot response time: {time.time() - start_time} seconds")
        #         return {"answer": response}

        # Xử lý truy vấn báo cáo
        report_pattern = r"(?:tiêu|spent)\s*(?:bao nhiêu|how much)\s*(?:cho|on)?\s*([\w\s]+)\s*(?:tháng|month)?\s*(\d{1,2})/(\d{4})"
        report_match = re.match(report_pattern, question.lower())
        if report_match:
            category_name = report_match.group(1).strip()
            month, year = int(report_match.group(2)), int(report_match.group(3))
            report_response = get_category_spending(db, current_user.id, category_name, month, year)
            crud.save_chat_message(db, current_user.id, str(uuid.uuid4()), question, report_response)
            logger.info(f"Chatbot response time: {time.time() - start_time} seconds")
            return {"answer": report_response}

        # Xử lý giao dịch
        transaction_response = await parse_transaction(question, current_user.id, db)
        if transaction_response:
            crud.save_chat_message(db, current_user.id, str(uuid.uuid4()), question, transaction_response)
            logger.info(f"Chatbot response time: {time.time() - start_time} seconds")
            return {"answer": transaction_response}

        # Tạo prompt cho OpenAI
        prompt = f"""
        Bạn là trợ lý tài chính vui tính.
        Tóm tắt chi tiêu: {summary}.
        Câu hỏi: {question}
        """

        # Gọi OpenAI
        try:
            response = await call_openai(prompt)
            if "choices" not in response:
                raise HTTPException(status_code=500, detail="Lỗi API OpenAI")
            answer = response["choices"][0]["message"]["content"]

            # Lưu lịch sử trò chuyện
            session_id = str(uuid.uuid4())
            crud.save_chat_message(db, current_user.id, session_id, question, answer)

            # Kiểm tra cảnh báo ngân sách
            for category_id, budget in summary["budgets"].items():
                if budget["spent"] > budget["limit"] * 1.2:
                    warning = f"Cảnh báo: Bạn tiêu hơi nhiều cho {budget['category_name']} rồi đấy! Tính ăn nhà hàng cả tháng hả?"
                    answer += f"\n{warning}"

            # Thêm đề xuất tối ưu chi tiêu
            suggestion = get_optimization_suggestion(summary)
            answer += f"\n{suggestion}"

            logger.info(f"Chatbot response time: {time.time() - start_time} seconds")
            if time.time() - start_time > 2:
                logger.warning("Chatbot response exceeded 2 seconds")

            return {"answer": answer}
        except Exception:
            fallback = "Tớ chưa hiểu lắm, bạn thử hỏi cách khác nhé!"
            crud.save_chat_message(db, current_user.id, str(uuid.uuid4()), question, fallback)
            logger.info(f"Chatbot response time: {time.time() - start_time} seconds")
            return {"answer": fallback}
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Lỗi: {str(e)}")