# schemas/report.py
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, Literal
from datetime import datetime
from uuid import UUID

class SavedReportBase(BaseModel):
    ReportName: str = Field(..., max_length=255)
    ReportType: Literal["daily", "weekly", "monthly", "yearly"]
    ReportConfig: Optional[Dict[str, Any]] = None

class SavedReportCreate(SavedReportBase):
    pass

class SavedReportUpdate(BaseModel):
    ReportName: Optional[str] = Field(None, max_length=255)
    ReportType: Optional[Literal["daily", "weekly", "monthly", "yearly"]] = None
    ReportConfig: Optional[Dict[str, Any]] = None

class SavedReportResponse(SavedReportBase):
    ReportID: UUID
    UserID: UUID
    LastGenerated: Optional[datetime] = None
    CreatedAt: datetime

    class Config:
        from_attributes = True

class FinancialOverview(BaseModel):
    TotalIncome: float = 0.0
    TotalExpense: float = 0.0
    NetAmount: float = 0.0
    TotalTransactions: int = 0

class FinancialOverviewRequest(BaseModel):
    StartDate: Optional[str] = None  # Format: YYYY-MM-DD
    EndDate: Optional[str] = None    # Format: YYYY-MM-DD