-- DỮ LIỆU MẪU
-- ===================================================================

INSERT INTO Categories (CategoryName, CategoryType, Icon, Color, IsDefault, SortOrder) VALUES 
(N'Thu nhập', 'income', 'money-bill-wave', '#22c55e', 1, 1),
(N'Chi tiêu thiết yếu', 'expense', 'home', '#ef4444', 1, 2),
(N'Chi tiêu giải trí', 'expense', 'gamepad', '#f59e0b', 1, 3),
(N'Đầu tư & Tiết kiệm', 'expense', 'chart-line', '#3b82f6', 1, 4);

DECLARE @IncomeID UNIQUEIDENTIFIER = (SELECT CategoryID FROM Categories WHERE CategoryName = N'Thu nhập');
DECLARE @EssentialID UNIQUEIDENTIFIER = (SELECT CategoryID FROM Categories WHERE CategoryName = N'Chi tiêu thiết yếu');
DECLARE @EntertainmentID UNIQUEIDENTIFIER = (SELECT CategoryID FROM Categories WHERE CategoryName = N'Chi tiêu giải trí');
DECLARE @InvestmentID UNIQUEIDENTIFIER = (SELECT CategoryID FROM Categories WHERE CategoryName = N'Đầu tư & Tiết kiệm');

INSERT INTO Categories (CategoryName, CategoryType, ParentCategoryID, Icon, IsDefault, SortOrder) VALUES 
(N'Lương', 'income', @IncomeID, 'wallet', 1, 1),
(N'Thưởng', 'income', @IncomeID, 'gift', 1, 2),
(N'Freelance', 'income', @IncomeID, 'laptop', 1, 3),
(N'Lợi nhuận đầu tư', 'income', @IncomeID, 'trending-up', 1, 4),

(N'Ăn uống', 'expense', @EssentialID, 'utensils', 1, 1),
(N'Tiền nhà', 'expense', @EssentialID, 'home', 1, 2),
(N'Giao thông', 'expense', @EssentialID, 'car', 1, 3),
(N'Y tế', 'expense', @EssentialID, 'stethoscope', 1, 4),
(N'Học phí', 'expense', @EssentialID, 'graduation-cap', 1, 5),

(N'Cafe & Trà sữa', 'expense', @EntertainmentID, 'coffee', 1, 1),
(N'Phim ảnh', 'expense', @EntertainmentID, 'film', 1, 2),
(N'Mua sắm', 'expense', @EntertainmentID, 'shopping-bag', 1, 3),
(N'Du lịch', 'expense', @EntertainmentID, 'plane', 1, 4),
(N'Game & Ứng dụng', 'expense', @EntertainmentID, 'gamepad', 1, 5),

(N'Tiết kiệm', 'expense', @InvestmentID, 'piggy-bank', 1, 1),
(N'Chứng khoán', 'expense', @InvestmentID, 'chart-line', 1, 2),
(N'Bất động sản', 'expense', @InvestmentID, 'building', 1, 3),
(N'Bảo hiểm', 'expense', @InvestmentID, 'shield', 1, 4);

-- User mẫu
INSERT INTO Users (Email, Password, FullName, Phone) VALUES 
('demo@gmail.com', 'demo123', N'Nguyễn Văn Demo', '0901234567'),
('user2@gmail.com', 'user123', N'Trần Thị B', '0901234568');

-- 3. Lấy UserID
DECLARE @UserID UNIQUEIDENTIFIER = (SELECT UserID FROM Users WHERE Email = 'demo@gmail.com');

-- 4. Tạo các bản ghi UserCategories cho người dùng từ các Category mặc định
INSERT INTO UserCategories (UserID, CategoryID, CustomName, IsActive)
SELECT @UserID, c.CategoryID, NULL, 1
FROM Categories c
WHERE c.IsDefault = 1;

-- 5. Lấy các UserCategoryID tương ứng
DECLARE @SalaryUCID UNIQUEIDENTIFIER = (
    SELECT uc.UserCategoryID FROM UserCategories uc
    JOIN Categories c ON uc.CategoryID = c.CategoryID
    WHERE uc.UserID = @UserID AND c.CategoryName = N'Lương'
);
DECLARE @FoodUCID UNIQUEIDENTIFIER = (
    SELECT uc.UserCategoryID FROM UserCategories uc
    JOIN Categories c ON uc.CategoryID = c.CategoryID
    WHERE uc.UserID = @UserID AND c.CategoryName = N'Ăn uống'
);
DECLARE @RentUCID UNIQUEIDENTIFIER = (
    SELECT uc.UserCategoryID FROM UserCategories uc
    JOIN Categories c ON uc.CategoryID = c.CategoryID
    WHERE uc.UserID = @UserID AND c.CategoryName = N'Tiền nhà'
);
DECLARE @TransportUCID UNIQUEIDENTIFIER = (
    SELECT uc.UserCategoryID FROM UserCategories uc
    JOIN Categories c ON uc.CategoryID = c.CategoryID
    WHERE uc.UserID = @UserID AND c.CategoryName = N'Giao thông'
);
DECLARE @CoffeeUCID UNIQUEIDENTIFIER = (
    SELECT uc.UserCategoryID FROM UserCategories uc
    JOIN Categories c ON uc.CategoryID = c.CategoryID
    WHERE uc.UserID = @UserID AND c.CategoryName = N'Cafe & Trà sữa'
);

-- 6. Thêm các giao dịch mẫu
INSERT INTO Transactions (UserID, UserCategoryID, TransactionType, Amount, Description, TransactionDate, PaymentMethod, CreatedBy)
VALUES 
(@UserID, @SalaryUCID, 'income', 15000000, N'Lương tháng 12/2024', '2024-12-01', N'Chuyển khoản', 'manual'),
(@UserID, @FoodUCID, 'expense', 150000, N'Ăn trưa', '2024-12-02', N'Tiền mặt', 'chatbot'),
(@UserID, @RentUCID, 'expense', 3000000, N'Tiền thuê nhà tháng 12', '2024-12-03', N'Chuyển khoản', 'manual'),
(@UserID, @TransportUCID, 'expense', 200000, N'Xăng xe', '2024-12-04', N'Thẻ ATM', 'manual'),
(@UserID, @CoffeeUCID, 'expense', 45000, N'Trà sữa', '2024-12-05', N'Tiền mặt', 'chatbot');

-- Tạo ngân sách tổng cho tháng 12/2024
DECLARE @BudgetID UNIQUEIDENTIFIER = NEWID();
INSERT INTO Budgets (
    BudgetID, UserID, BudgetName, BudgetType, Amount, PeriodStart, PeriodEnd, 
    AutoAdjust, IncludeIncome, AlertThreshold, IsActive
)
VALUES (
    @BudgetID, @UserID, N'Ngân sách tháng 12/2024', 'monthly', 10000000,
    '2024-12-01', '2024-12-31',
    1, 0, 80.0, 1
);

-- Phân bổ danh mục con (BudgetCategories)
INSERT INTO BudgetCategories (BudgetID, UserCategoryID, AllocatedAmount, SpentAmount)
VALUES 
(@BudgetID, @FoodUCID, 3000000, 2500000),
(@BudgetID, @RentUCID, 3500000, 3500000),
(@BudgetID, @TransportUCID, 2000000, 1800000),
(@BudgetID, @CoffeeUCID, 1500000, 1450000);

-- Tạo cảnh báo giả định (BudgetAlerts)
INSERT INTO BudgetAlerts (
    BudgetID, UserID, AlertType, CurrentAmount, BudgetAmount, PercentageUsed, Message
)
VALUES 
(@BudgetID, @UserID, 'warning', 8000000, 10000000, 80.00, N'Bạn đã sử dụng 80% ngân sách tháng 12/2024 cho toàn bộ chi tiêu');



-- Report mẫu
INSERT INTO SavedReports (UserID, ReportName, ReportType, ReportConfig, Description) VALUES 
(@UserID, N'Báo cáo chi tiêu hàng tháng', 'monthly_summary', 
 '{"dateRange":"current_month","categories":"all","groupBy":"category","showBudget":true}', 
 N'Tổng hợp chi tiêu theo danh mục trong tháng hiện tại'),
(@UserID, N'Phân tích ngân sách', 'budget_tracking', 
 '{"month":12,"year":2024,"showAlert":true,"compareWithPrevious":true}', 
 N'Theo dõi tình hình sử dụng ngân sách tháng 12/2024'),
(@UserID, N'Thu chi theo quý', 'income_expense', 
 '{"period":"quarterly","year":2024,"quarter":4,"showTrend":true}', 
 N'Báo cáo thu chi quý IV/2024 với xu hướng'),
(@UserID, N'Top danh mục chi nhiều nhất', 'category_analysis', 
 '{"period":"monthly","limit":5,"sortBy":"amount","order":"desc"}', 
 N'Top 5 danh mục chi tiêu nhiều nhất trong tháng');


 -- Chat session mẫu
INSERT INTO ChatSessions (UserID, SessionName) VALUES 
(@UserID, N'Hỏi về chi tiêu tháng này');

DECLARE @SessionID INT = SCOPE_IDENTITY();

INSERT INTO ChatMessages (SessionID, UserID, MessageType, Content, Intent, ActionTaken) VALUES 
(@SessionID, @UserID, 'user', N'Tôi chi bao nhiêu tiền cho ăn uống tháng này?', 'query_expense', NULL),
(@SessionID, @UserID, 'bot', N'Bạn đã chi 150,000 VND cho ăn uống trong tháng 12/2024. Ngân sách của bạn cho mục này là 5,000,000 VND, còn lại 4,850,000 VND.', 'expense_summary', 'get_expense_by_category'),
(@SessionID, @UserID, 'user', N'Thêm giao dịch: mua cafe 35000', 'add_transaction', NULL),
(@SessionID, @UserID, 'bot', N'Đã thêm giao dịch: Chi 35,000 VND cho Cafe & Trà sữa. Giao dịch được tự động phân loại.', 'transaction_added', 'add_transaction');