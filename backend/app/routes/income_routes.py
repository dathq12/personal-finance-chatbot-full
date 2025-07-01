from fastapi import APIRouter

router = APIRouter(prefix="/incomes", tags=["Incomes"])

@router.get("/ping")
def ping():
    return {"message": "Income router is working"}
