from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.config import settings
import urllib

params = urllib.parse.quote_plus(
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=DESKTOP-2SS6FHK\\SQLEXPRESS;"
    "DATABASE=FinanceChatbotDB;"
    "Trusted_Connection=yes;"
    "TrustServerCertificate=yes;"
    "MARS_Connection=yes;"
    "charset=utf8;"
)


# Lấy URL kết nối từ biến môi trường
# params = urllib.parse.quote_plus(settings.DATABASE_URL)
# Lấy DATABASE_URL gốc từ .env (chỉ chứa phần odbc_connect=...)
# Ví dụ trong .env:
# DATABASE_URL=DRIVER={ODBC Driver 17 for SQL Server};SERVER=localhost,1433;DATABASE=FinanceChatbotDB;Trusted_Connection=yes
# Encode lại để tránh lỗi dấu { } ; và khoảng trắng
params = urllib.parse.quote_plus(settings.DATABASE_URL)


# Tạo URL kết nối đầy đủ cho SQLAlchemy
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
