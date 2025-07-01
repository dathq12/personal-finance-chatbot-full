import openai
from app.config import settings

openai.api_key = settings.OPENAI_API_KEY

def ask_gpt(prompt: str):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )
    return response['choices'][0]['message']['content']