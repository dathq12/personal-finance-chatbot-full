from fastapi import APIRouter

router = APIRouter(prefix="/categories", tags=["Categories"])

@router.get("/ping")
def ping():
    return {"message": "Category router is working"}
