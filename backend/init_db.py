from app.database import engine
from app.models import user_model  # Import tất cả các model

user_model.Base.metadata.create_all(bind=engine)

print("✅ Khởi tạo bảng SQL Server thành công.")
