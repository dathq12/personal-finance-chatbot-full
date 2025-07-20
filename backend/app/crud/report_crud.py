# crud/report.py
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Optional
from uuid import UUID
from datetime import date
import json

from models.report import SavedReport
from schemas.report_schema import SavedReportCreate, SavedReportUpdate, FinancialOverview

class ReportCRUD:
    def __init__(self, db: Session):
        self.db = db

    def create_saved_report(self, user_id: UUID, report_data: SavedReportCreate) -> SavedReport:
        """Tạo báo cáo mới"""
        db_report = SavedReport(
            UserID=user_id,
            ReportName=report_data.ReportName,
            ReportType=report_data.ReportType,
            ReportConfig=json.dumps(report_data.ReportConfig) if report_data.ReportConfig else None
        )
        self.db.add(db_report)
        self.db.commit()
        self.db.refresh(db_report)
        return db_report

    def get_saved_reports(self, user_id: UUID, skip: int = 0, limit: int = 100) -> List[SavedReport]:
        """Lấy danh sách báo cáo đã lưu của user"""
        return self.db.query(SavedReport)\
                     .filter(SavedReport.UserID == user_id)\
                     .offset(skip)\
                     .limit(limit)\
                     .all()

    def get_saved_report_by_id(self, user_id: UUID, report_id: UUID) -> Optional[SavedReport]:
        """Lấy báo cáo theo ID"""
        return self.db.query(SavedReport)\
                     .filter(SavedReport.UserID == user_id, 
                            SavedReport.ReportID == report_id)\
                     .first()

    def update_saved_report(self, user_id: UUID, report_id: UUID, report_data: SavedReportUpdate) -> Optional[SavedReport]:
        """Cập nhật báo cáo"""
        db_report = self.get_saved_report_by_id(user_id, report_id)
        if not db_report:
            return None
        
        update_data = report_data.dict(exclude_unset=True)
        
        # Xử lý ReportConfig thành JSON string
        if 'ReportConfig' in update_data and update_data['ReportConfig'] is not None:
            update_data['ReportConfig'] = json.dumps(update_data['ReportConfig'])
        
        for field, value in update_data.items():
            setattr(db_report, field, value)
        
        self.db.commit()
        self.db.refresh(db_report)
        return db_report

    def delete_saved_report(self, user_id: UUID, report_id: UUID) -> bool:
        """Xóa báo cáo"""
        db_report = self.get_saved_report_by_id(user_id, report_id)
        if not db_report:
            return False
        
        self.db.delete(db_report)
        self.db.commit()
        return True

    def get_financial_overview(self, user_id: UUID, start_date: Optional[str] = None, 
                             end_date: Optional[str] = None) -> FinancialOverview:
        """Gọi stored procedure GetUserFinancialOverview"""
        try:
            # Tạo câu lệnh SQL để gọi stored procedure
            sql = text("""
                EXEC GetUserFinancialOverview 
                    @UserID = :user_id,
                    @StartDate = :start_date,
                    @EndDate = :end_date
            """)
            
            # Execute stored procedure
            result = self.db.execute(
                sql, 
                {
                    "user_id": str(user_id),
                    "start_date": start_date,
                    "end_date": end_date
                }
            ).fetchone()
            
            if result:
                return FinancialOverview(
                    TotalIncome=float(result.TotalIncome or 0),
                    TotalExpense=float(result.TotalExpense or 0),
                    NetAmount=float(result.NetAmount or 0),
                    TotalTransactions=int(result.TotalTransactions or 0)
                )
            else:
                return FinancialOverview()
                
        except Exception as e:
            print(f"Error calling stored procedure: {e}")
            return FinancialOverview()

    def update_last_generated(self, report_id: UUID):
        """Cập nhật thời gian generate báo cáo cuối cùng"""
        try:
            sql = text("""
                UPDATE SavedReports 
                SET LastGenerated = GETDATE() 
                WHERE ReportID = :report_id
            """)
            
            self.db.execute(sql, {"report_id": str(report_id)})
            self.db.commit()
        except Exception as e:
            print(f"Error updating last generated: {e}")