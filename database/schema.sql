-- DATABASE SCHEMA: HỆ THỐNG QUẢN LÝ TÀI CHÍNH CÁ NHÂN - SQL SERVER
-- ===================================================================

-- CREATE DATABASE PersonalFinanceApp;
-- USE PersonalFinanceApp;

-- 1. BẢNG QUẢN LÝ NGƯỜI DÙNG
-- ===================================================================

CREATE TABLE Users (
    UserID UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
    Email NVARCHAR(255) UNIQUE NOT NULL,
    PasswordHash NVARCHAR(255) NOT NULL,
    FullName NVARCHAR(255) NOT NULL,
    Phone NVARCHAR(20),
    AvatarURL NVARCHAR(500),
    TimeZone NVARCHAR(50) DEFAULT 'SE Asia Standard Time',
    Currency NCHAR(3) DEFAULT 'VND',
    IsActive BIT DEFAULT 1,
    EmailVerified BIT DEFAULT 0,
    CreatedAt DATETIME2 DEFAULT GETDATE(),
    UpdatedAt DATETIME2 DEFAULT GETDATE(),
    LastLogin DATETIME2
);

CREATE TABLE UserSessions (
    SessionID UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
    UserID UNIQUEIDENTIFIER NOT NULL REFERENCES Users(UserID) ON DELETE CASCADE,
    RefreshToken NVARCHAR(500) NOT NULL,
    DeviceInfo NVARCHAR(MAX),
    IPAddress NVARCHAR(45),
    ExpiresAt DATETIME2 NOT NULL,
    CreatedAt DATETIME2 DEFAULT GETDATE()
);

-- 2. DANH MỤC
-- ===================================================================

CREATE TABLE Categories (
    CategoryID UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
    CategoryName NVARCHAR(100) NOT NULL,
    CategoryType NVARCHAR(20) NOT NULL CHECK (CategoryType IN ('income', 'expense')),
    ParentCategoryID UNIQUEIDENTIFIER REFERENCES Categories(CategoryID),
    Description NVARCHAR(500),
    Icon NVARCHAR(50),
    Color NVARCHAR(7),
    IsDefault BIT DEFAULT 0,
    IsActive BIT DEFAULT 1,
    SortOrder INT DEFAULT 0,
    CreatedAt DATETIME2 DEFAULT GETDATE()
);

CREATE TABLE UserCategories (
    UserCategoryID UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
    UserID UNIQUEIDENTIFIER NOT NULL REFERENCES Users(UserID) ON DELETE CASCADE,
    CategoryID UNIQUEIDENTIFIER NOT NULL REFERENCES Categories(CategoryID),
    CustomName NVARCHAR(100),
    IsActive BIT DEFAULT 1,
    CreatedAt DATETIME2 DEFAULT GETDATE(),
    UNIQUE(UserID, CategoryID)
);

-- 3. GIAO DỊCH
-- ===================================================================

CREATE TABLE Transactions (
    TransactionID UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
    UserID UNIQUEIDENTIFIER NOT NULL REFERENCES Users(UserID) ON DELETE CASCADE,
    CategoryID UNIQUEIDENTIFIER NOT NULL REFERENCES Categories(CategoryID),
    TransactionType NVARCHAR(20) NOT NULL CHECK (TransactionType IN ('income', 'expense')),
    Amount DECIMAL(15,2) NOT NULL CHECK (Amount > 0),
    Description NVARCHAR(500),
    TransactionDate DATE NOT NULL,
    TransactionTime TIME DEFAULT CONVERT(TIME, GETDATE()),
    PaymentMethod NVARCHAR(50),
    Location NVARCHAR(255),
    Tags NVARCHAR(MAX),
    ReceiptURL NVARCHAR(500),
    Notes NVARCHAR(MAX),
    IsRecurring BIT DEFAULT 0,
    RecurringPattern NVARCHAR(MAX),
    CreatedAt DATETIME2 DEFAULT GETDATE(),
    UpdatedAt DATETIME2 DEFAULT GETDATE(),
    CreatedBy NVARCHAR(20) DEFAULT 'manual' CHECK (CreatedBy IN ('manual', 'chatbot', 'import', 'recurring'))
);

-- 4. NGÂN SÁCH
-- ===================================================================

CREATE TABLE Budgets (
    BudgetID UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
    UserID UNIQUEIDENTIFIER NOT NULL REFERENCES Users(UserID) ON DELETE CASCADE,
    CategoryID UNIQUEIDENTIFIER REFERENCES Categories(CategoryID),
    BudgetName NVARCHAR(255) NOT NULL,
    BudgetType NVARCHAR(20) NOT NULL CHECK (BudgetType IN ('monthly', 'weekly', 'yearly')),
    Amount DECIMAL(15,2) NOT NULL CHECK (Amount > 0),
    PeriodStart DATE NOT NULL,
    PeriodEnd DATE NOT NULL,
    AlertThreshold DECIMAL(5,2) DEFAULT 80.00 CHECK (AlertThreshold BETWEEN 0 AND 100),
    IsActive BIT DEFAULT 1,
    CreatedAt DATETIME2 DEFAULT GETDATE(),
    UpdatedAt DATETIME2 DEFAULT GETDATE()
);

CREATE TABLE BudgetAlerts (
    AlertID UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
    BudgetID UNIQUEIDENTIFIER NOT NULL REFERENCES Budgets(BudgetID) ON DELETE CASCADE,
    UserID UNIQUEIDENTIFIER NOT NULL REFERENCES Users(UserID) ON DELETE CASCADE,
    AlertType NVARCHAR(20) NOT NULL CHECK (AlertType IN ('warning', 'exceeded', 'near_limit')),
    CurrentAmount DECIMAL(15,2) NOT NULL,
    BudgetAmount DECIMAL(15,2) NOT NULL,
    PercentageUsed DECIMAL(5,2) NOT NULL,
    Message NVARCHAR(MAX),
    IsRead BIT DEFAULT 0,
    CreatedAt DATETIME2 DEFAULT GETDATE()
);

-- 5. CHATBOT
-- ===================================================================

CREATE TABLE ChatSessions (
    SessionID UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
    UserID UNIQUEIDENTIFIER NOT NULL REFERENCES Users(UserID) ON DELETE CASCADE,
    SessionName NVARCHAR(255),
    StartedAt DATETIME2 DEFAULT GETDATE(),
    EndedAt DATETIME2,
    IsActive BIT DEFAULT 1,
    MessageCount INT DEFAULT 0
);

CREATE TABLE ChatMessages (
    MessageID UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
    SessionID UNIQUEIDENTIFIER NOT NULL REFERENCES ChatSessions(SessionID) ON DELETE CASCADE,
    UserID UNIQUEIDENTIFIER NOT NULL REFERENCES Users(UserID) ON DELETE CASCADE,
    MessageType NVARCHAR(20) NOT NULL CHECK (MessageType IN ('user', 'bot', 'system')),
    Content NVARCHAR(MAX) NOT NULL,
    Intent NVARCHAR(50),
    ActionTaken NVARCHAR(50),
    CreatedAt DATETIME2 DEFAULT GETDATE()
);

-- 6. REPORTS
-- ===================================================================

CREATE TABLE SavedReports (
    ReportID UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
    UserID UNIQUEIDENTIFIER NOT NULL REFERENCES Users(UserID) ON DELETE CASCADE,
    ReportName NVARCHAR(255) NOT NULL,
    ReportType NVARCHAR(50) NOT NULL,
    ReportConfig NVARCHAR(MAX),
    LastGenerated DATETIME2,
    CreatedAt DATETIME2 DEFAULT GETDATE()
);

-- 7. AUDIT LOGS
-- ===================================================================

CREATE TABLE AuditLogs (
    AuditID UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
    UserID UNIQUEIDENTIFIER REFERENCES Users(UserID),
    TableName NVARCHAR(50) NOT NULL,
    RecordID UNIQUEIDENTIFIER NOT NULL,
    Action NVARCHAR(20) NOT NULL CHECK (Action IN ('INSERT', 'UPDATE', 'DELETE')),
    OldValues NVARCHAR(MAX),
    NewValues NVARCHAR(MAX),
    IPAddress NVARCHAR(45),
    CreatedAt DATETIME2 DEFAULT GETDATE()
);

-- TRIGGERS
-- ===================================================================

CREATE TRIGGER TR_Users_UpdatedAt ON Users AFTER UPDATE AS
BEGIN
    SET NOCOUNT ON;
    UPDATE Users SET UpdatedAt = GETDATE()
    WHERE UserID IN (SELECT UserID FROM inserted);
END;

CREATE TRIGGER TR_Transactions_UpdatedAt ON Transactions AFTER UPDATE AS
BEGIN
    SET NOCOUNT ON;
    UPDATE Transactions SET UpdatedAt = GETDATE()
    WHERE TransactionID IN (SELECT TransactionID FROM inserted);
END;

CREATE TRIGGER TR_Budgets_UpdatedAt ON Budgets AFTER UPDATE AS
BEGIN
    SET NOCOUNT ON;
    UPDATE Budgets SET UpdatedAt = GETDATE()
    WHERE BudgetID IN (SELECT BudgetID FROM inserted);
END;

CREATE TRIGGER TR_ChatMessages_UpdateCount ON ChatMessages AFTER INSERT AS
BEGIN
    SET NOCOUNT ON;
    UPDATE ChatSessions SET MessageCount = MessageCount + 1
    WHERE SessionID IN (SELECT SessionID FROM inserted);
END;

-- INDEXES
-- ===================================================================

CREATE INDEX IX_Users_Email ON Users(Email);
CREATE INDEX IX_Users_Active ON Users(IsActive);

CREATE INDEX IX_Categories_Type ON Categories(CategoryType);
CREATE INDEX IX_Categories_Parent ON Categories(ParentCategoryID);

CREATE INDEX IX_Transactions_UserID_Date ON Transactions(UserID, TransactionDate DESC);
CREATE INDEX IX_Transactions_CategoryID ON Transactions(CategoryID);
CREATE INDEX IX_Transactions_Type ON Transactions(TransactionType);

CREATE INDEX IX_Budgets_User_Active ON Budgets(UserID, IsActive);
CREATE INDEX IX_Budgets_Period ON Budgets(PeriodStart, PeriodEnd);

CREATE INDEX IX_BudgetAlerts_User_Read ON BudgetAlerts(UserID, IsRead);

CREATE INDEX IX_ChatMessages_Session ON ChatMessages(SessionID);
CREATE INDEX IX_ChatMessages_User ON ChatMessages(UserID);
CREATE INDEX IX_ChatMessages_Created ON ChatMessages(CreatedAt DESC);

-- FUNCTION
-- ===================================================================

CREATE FUNCTION GetCategoryFullName(@CategoryID UNIQUEIDENTIFIER)
RETURNS NVARCHAR(255)
AS
BEGIN
    DECLARE @Result NVARCHAR(255), @ParentName NVARCHAR(100), @CategoryName NVARCHAR(100);
    SELECT @CategoryName = CategoryName, @ParentName = p.CategoryName
    FROM Categories c
    LEFT JOIN Categories p ON c.ParentCategoryID = p.CategoryID
    WHERE c.CategoryID = @CategoryID;
    SET @Result = CASE 
        WHEN @ParentName IS NOT NULL THEN @ParentName + ' > ' + @CategoryName
        ELSE @CategoryName
    END;
    RETURN @Result;
END;

-- STORED PROCEDURE
-- ===================================================================

CREATE PROCEDURE GetUserFinancialOverview
    @UserID UNIQUEIDENTIFIER,
    @StartDate DATE = NULL,
    @EndDate DATE = NULL
AS
BEGIN
    SET NOCOUNT ON;
    IF @StartDate IS NULL SET @StartDate = DATEFROMPARTS(YEAR(GETDATE()), MONTH(GETDATE()), 1);
    IF @EndDate IS NULL SET @EndDate = EOMONTH(GETDATE());
    SELECT 
        SUM(CASE WHEN TransactionType = 'income' THEN Amount ELSE 0 END) as TotalIncome,
        SUM(CASE WHEN TransactionType = 'expense' THEN Amount ELSE 0 END) as TotalExpense,
        SUM(CASE WHEN TransactionType = 'income' THEN Amount ELSE -Amount END) as NetAmount,
        COUNT(*) as TotalTransactions
    FROM Transactions 
    WHERE UserID = @UserID 
    AND TransactionDate BETWEEN @StartDate AND @EndDate;
END;

CREATE PROCEDURE CheckBudgetStatus
    @UserID UNIQUEIDENTIFIER,
    @BudgetID UNIQUEIDENTIFIER = NULL
AS
BEGIN
    SET NOCOUNT ON;
    SELECT 
        b.BudgetID,
        b.BudgetName,
        b.Amount as BudgetAmount,
        ISNULL(SUM(t.Amount), 0) as SpentAmount,
        (ISNULL(SUM(t.Amount), 0) / b.Amount * 100) as PercentageUsed,
        CASE 
            WHEN (ISNULL(SUM(t.Amount), 0) / b.Amount * 100) >= 100 THEN 'exceeded'
            WHEN (ISNULL(SUM(t.Amount), 0) / b.Amount * 100) >= b.AlertThreshold THEN 'warning'
            ELSE 'normal'
        END as Status
    FROM Budgets b
    LEFT JOIN Transactions t ON b.CategoryID = t.CategoryID 
        AND t.UserID = b.UserID
        AND t.TransactionDate BETWEEN b.PeriodStart AND b.PeriodEnd
        AND t.TransactionType = 'expense'
    WHERE b.UserID = @UserID 
    AND b.IsActive = 1
    AND (@BudgetID IS NULL OR b.BudgetID = @BudgetID)
    GROUP BY b.BudgetID, b.BudgetName, b.Amount, b.AlertThreshold;
END;

-- DỮ LIỆU MẪU
-- ===================================================================

INSERT INTO Categories (CategoryName, CategoryType, Icon, Color, IsDefault, SortOrder) VALUES 
('Thu nhập', 'income', 'money-bill-wave', '#22c55e', 1, 1),
('Chi tiêu thiết yếu', 'expense', 'home', '#ef4444', 1, 2),
('Chi tiêu giải trí', 'expense', 'gamepad', '#f59e0b', 1, 3),
('Đầu tư & Tiết kiệm', 'expense', 'chart-line', '#3b82f6', 1, 4);

DECLARE @IncomeID UNIQUEIDENTIFIER = (SELECT CategoryID FROM Categories WHERE CategoryName = 'Thu nhập');
DECLARE @EssentialID UNIQUEIDENTIFIER = (SELECT CategoryID FROM Categories WHERE CategoryName = 'Chi tiêu thiết yếu');
DECLARE @EntertainmentID UNIQUEIDENTIFIER = (SELECT CategoryID FROM Categories WHERE CategoryName = 'Chi tiêu giải trí');
DECLARE @InvestmentID UNIQUEIDENTIFIER = (SELECT CategoryID FROM Categories WHERE CategoryName = 'Đầu tư & Tiết kiệm');

INSERT INTO Categories (CategoryName, CategoryType, ParentCategoryID, Icon, IsDefault, SortOrder) VALUES 
('Lương', 'income', @IncomeID, 'wallet', 1, 1),
('Thưởng', 'income', @IncomeID, 'gift', 1, 2),
('Freelance', 'income', @IncomeID, 'laptop', 1, 3),
('Lợi nhuận đầu tư', 'income', @IncomeID, 'trending-up', 1, 4),

('Ăn uống', 'expense', @EssentialID, 'utensils', 1, 1),
('Tiền nhà', 'expense', @EssentialID, 'home', 1, 2),
('Giao thông', 'expense', @EssentialID, 'car', 1, 3),
('Y tế', 'expense', @EssentialID, 'stethoscope', 1, 4),
('Học phí', 'expense', @EssentialID, 'graduation-cap', 1, 5),

('Cafe & Trà sữa', 'expense', @EntertainmentID, 'coffee', 1, 1),
('Phim ảnh', 'expense', @EntertainmentID, 'film', 1, 2),
('Mua sắm', 'expense', @EntertainmentID, 'shopping-bag', 1, 3),
('Du lịch', 'expense', @EntertainmentID, 'plane', 1, 4),
('Game & Ứng dụng', 'expense', @EntertainmentID, 'gamepad', 1, 5),

('Tiết kiệm', 'expense', @InvestmentID, 'piggy-bank', 1, 1),
('Chứng khoán', 'expense', @InvestmentID, 'chart-line', 1, 2),
('Bất động sản', 'expense', @InvestmentID, 'building', 1, 3),
('Bảo hiểm', 'expense', @InvestmentID, 'shield', 1, 4);
