from fastapi import APIRouter

router = APIRouter(prefix="/budgets", tags=["Budgets"])

@router.get("/ping")
def ping():
    return {"message": "Budget router is working"}
