from fastapi import APIRouter
from app.utils.gpt_client import ask_gpt

router = APIRouter(prefix="/chatbot", tags=["Chatbot"])

@router.post("/ask")
def ask(prompt: str):
    response = ask_gpt(prompt)
    return {"response": response}
