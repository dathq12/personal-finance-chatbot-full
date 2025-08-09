from sqlalchemy import create_engine, text
import urllib

params = urllib.parse.quote_plus(
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=DESKTOP-2SS6FHK\\SQLEXPRESS;"
    "DATABASE=FinanceChatbotDB;"
    "Trusted_Connection=yes;"
)


db_url = f"mssql+pyodbc:///?odbc_connect={params}"
engine = create_engine(db_url)

try:
    with engine.connect() as conn:
        result = conn.execute(text("SELECT GETDATE()"))  # 👈 dùng text()
        print("✅ Kết nối thành công:", result.scalar())
except Exception as e:
    print("❌ Lỗi kết nối:", e)
