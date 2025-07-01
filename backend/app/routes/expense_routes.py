from fastapi import APIRouter

router = APIRouter(prefix="/expenses", tags=["Expenses"])

@router.get("/ping")
def ping():
    return {"message": "Expense router is working"}
