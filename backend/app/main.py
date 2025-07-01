from fastapi import FastAPI
from app.routes import auth_routes, chatbot_routes, category_routes, budget_routes, income_routes, expense_routes

print("[DEBUG] Module path:", category_routes.__file__)
print("[DEBUG] Available attributes in module:", dir(category_routes))

app = FastAPI()

app.include_router(auth_routes.router)
app.include_router(chatbot_routes.router)
app.include_router(category_routes.router)
app.include_router(budget_routes.router)
app.include_router(income_routes.router)
app.include_router(expense_routes.router)
