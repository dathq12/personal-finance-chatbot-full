import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import urllib

# Load biến môi trường từ file .env
load_dotenv()

# Lấy chuỗi kết nối từ biến môi trường
db_url = os.getenv("DATABASE_URL")

# Nếu bạn muốn hỗ trợ username/password thay vì Trusted_Connection
# uncomment và chỉnh lại:
# username = "sa"
# password = "your_password"
# params = urllib.parse.quote_plus(
#     f"DRIVER={{ODBC Driver 17 for SQL Server}};"
#     f"SERVER=localhost,1433;"
#     f"DATABASE=FinanceChatbotDB;"
#     f"UID={username};PWD={password}"
# )
# db_url = f"mssql+pyodbc:///?odbc_connect={params}"

# Tạo engine
engine = create_engine(db_url)

# Thử kết nối
try:
    with engine.connect() as conn:
        result = conn.execute(text("SELECT GETDATE()"))
        print("✅ Kết nối thành công:", result.scalar())
except Exception as e:
    print("❌ Lỗi kết nối:", e)
