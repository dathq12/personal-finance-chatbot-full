# routers/report.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from database import get_db
from schemas.report_schema import (
    SavedReportCreate, SavedReportUpdate, SavedReportResponse,
    FinancialOverview, FinancialOverviewRequest
)
from crud.report_crud import ReportCRUD
from dependencies import get_current_user  # Giả sử bạn có authentication

router = APIRouter(prefix="/reports", tags=["reports"])

@router.post("/", response_model=SavedReportResponse, status_code=status.HTTP_201_CREATED)
def create_saved_report(
    report_data: SavedReportCreate,
    db: Session = Depends(get_db),
    current_user_id: UUID = Depends(get_current_user)
):
    """Tạo báo cáo mới"""
    crud = ReportCRUD(db)
    return crud.create_saved_report(current_user_id, report_data)

@router.get("/", response_model=List[SavedReportResponse])
def get_saved_reports(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user_id: UUID = Depends(get_current_user)
):
    """Lấy danh sách báo cáo đã lưu"""
    crud = ReportCRUD(db)
    reports = crud.get_saved_reports(current_user_id, skip, limit)
    
    # Convert ReportConfig từ JSON string về dict
    for report in reports:
        if report.ReportConfig:
            try:
                import json
                report.ReportConfig = json.loads(report.ReportConfig)
            except:
                report.ReportConfig = {}
    
    return reports

@router.get("/{report_id}", response_model=SavedReportResponse)
def get_saved_report(
    report_id: UUID,
    db: Session = Depends(get_db),
    current_user_id: UUID = Depends(get_current_user)
):
    """Lấy báo cáo theo ID"""
    crud = ReportCRUD(db)
    report = crud.get_saved_report_by_id(current_user_id, report_id)
    
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found"
        )
    
    # Convert ReportConfig từ JSON string về dict
    if report.ReportConfig:
        try:
            import json
            report.ReportConfig = json.loads(report.ReportConfig)
        except:
            report.ReportConfig = {}
    
    return report

@router.put("/{report_id}", response_model=SavedReportResponse)
def update_saved_report(
    report_id: UUID,
    report_data: SavedReportUpdate,
    db: Session = Depends(get_db),
    current_user_id: UUID = Depends(get_current_user)
):
    """Cập nhật báo cáo"""
    crud = ReportCRUD(db)
    report = crud.update_saved_report(current_user_id, report_id, report_data)
    
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found"
        )
    
    # Convert ReportConfig từ JSON string về dict
    if report.ReportConfig:
        try:
            import json
            report.ReportConfig = json.loads(report.ReportConfig)
        except:
            report.ReportConfig = {}
    
    return report

@router.delete("/{report_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_saved_report(
    report_id: UUID,
    db: Session = Depends(get_db),
    current_user_id: UUID = Depends(get_current_user)
):
    """Xóa báo cáo"""
    crud = ReportCRUD(db)
    success = crud.delete_saved_report(current_user_id, report_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found"
        )

@router.post("/financial-overview", response_model=FinancialOverview)
def get_financial_overview(
    request: FinancialOverviewRequest,
    db: Session = Depends(get_db),
    current_user_id: UUID = Depends(get_current_user)
):
    """Lấy tổng quan tài chính sử dụng stored procedure"""
    crud = ReportCRUD(db)
    return crud.get_financial_overview(
        current_user_id, 
        request.StartDate, 
        request.EndDate
    )

@router.post("/{report_id}/generate")
def generate_report(
    report_id: UUID,
    request: FinancialOverviewRequest,
    db: Session = Depends(get_db),
    current_user_id: UUID = Depends(get_current_user)
):
    """Generate báo cáo và cập nhật LastGenerated"""
    crud = ReportCRUD(db)
    
    # Kiểm tra báo cáo có tồn tại không
    report = crud.get_saved_report_by_id(current_user_id, report_id)
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found"
        )
    
    # Lấy dữ liệu tài chính
    financial_data = crud.get_financial_overview(
        current_user_id, 
        request.StartDate, 
        request.EndDate
    )
    
    # Cập nhật LastGenerated
    crud.update_last_generated(report_id)
    
    return {
        "report_info": report,
        "financial_data": financial_data,
        "generated_at": "now"
    }