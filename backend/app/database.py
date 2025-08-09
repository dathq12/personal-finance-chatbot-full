from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.config import settings
import urllib

params = urllib.parse.quote_plus(
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=DESKTOP-2SS6FHK\\SQLEXPRESS;"
    "DATABASE=FinanceChatbotDB;"
    "Trusted_Connection=yes;"
)

# Lấy URL kết nối từ biến môi trường
# params = urllib.parse.quote_plus(settings.DATABASE_URL)


# Kết nối qua pyodbc
DATABASE_URL = f"mssql+pyodbc:///?odbc_connect={params}"

# Create engine & session
engine = create_engine(DATABASE_URL, echo=True, fast_executemany=True)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
Base = declarative_base()

# Database dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
