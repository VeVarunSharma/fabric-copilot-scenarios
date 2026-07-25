DROP TABLE IF EXISTS dbo.FactFinancialPosting;
DROP TABLE IF EXISTS dbo.DimBusinessUnit;

CREATE TABLE dbo.DimBusinessUnit (
    BusinessUnitCode NVARCHAR(20) NOT NULL,
    BusinessUnitName NVARCHAR(100) NOT NULL,
    RegionName NVARCHAR(50) NOT NULL,
    IsActive BIT NOT NULL
);

CREATE TABLE dbo.FactFinancialPosting (
    PostingId BIGINT NOT NULL,
    FiscalYear INT NOT NULL,
    FiscalMonth INT NOT NULL,
    BusinessUnitCode NVARCHAR(20) NOT NULL,
    ScenarioName NVARCHAR(20) NOT NULL,
    AccountCategory NVARCHAR(20) NOT NULL,
    Amount DECIMAL(18, 2) NOT NULL,
    PostingDate DATE NOT NULL,
    CostCenterCode NVARCHAR(20) NOT NULL
);

INSERT INTO dbo.DimBusinessUnit (
    BusinessUnitCode,
    BusinessUnitName,
    RegionName,
    IsActive
)
VALUES
    ('NA-RETAIL', 'North America Stores', 'North America', 1),
    ('NA-ECOM', 'North America Digital', 'North America', 1),
    ('NA-LEGACY', 'North America Legacy', 'North America', 0),
    ('EU-STORE', 'Europe Stores', 'Europe', 1);

INSERT INTO dbo.FactFinancialPosting (
    PostingId,
    FiscalYear,
    FiscalMonth,
    BusinessUnitCode,
    ScenarioName,
    AccountCategory,
    Amount,
    PostingDate,
    CostCenterCode
)
VALUES
    (1, 2026, 1, 'NA-RETAIL', 'Actual', 'Revenue', 1200000.00, '2026-01-31', 'CC100'),
    (2, 2026, 1, 'NA-RETAIL', 'Actual', 'Expense', 900000.00, '2026-01-31', 'CC100'),
    (3, 2026, 1, 'NA-RETAIL', 'Budget', 'Revenue', 1100000.00, '2026-01-31', 'CC100'),
    (4, 2026, 1, 'NA-RETAIL', 'Budget', 'Expense', 880000.00, '2026-01-31', 'CC100'),
    (5, 2026, 2, 'NA-RETAIL', 'Actual', 'Revenue', 1250000.00, '2026-02-28', 'CC100'),
    (6, 2026, 2, 'NA-RETAIL', 'Actual', 'Expense', 910000.00, '2026-02-28', 'CC100'),
    (7, 2026, 2, 'NA-RETAIL', 'Budget', 'Revenue', 1250000.00, '2026-02-28', 'CC100'),
    (8, 2026, 2, 'NA-RETAIL', 'Budget', 'Expense', 0.00, '2026-02-28', 'CC100'),
    (9, 2026, 1, 'NA-ECOM', 'Actual', 'Revenue', 980000.00, '2026-01-31', 'CC200'),
    (10, 2026, 1, 'NA-ECOM', 'Actual', 'Expense', 650000.00, '2026-01-31', 'CC200'),
    (11, 2026, 1, 'NA-ECOM', 'Budget', 'Revenue', 1000000.00, '2026-01-31', 'CC200'),
    (12, 2026, 1, 'NA-ECOM', 'Budget', 'Expense', 640000.00, '2026-01-31', 'CC200'),
    (13, 2026, 2, 'NA-ECOM', 'Actual', 'Revenue', 1010000.00, '2026-02-28', 'CC200'),
    (14, 2026, 2, 'NA-ECOM', 'Actual', 'Expense', 670000.00, '2026-02-28', 'CC200'),
    (15, 2026, 2, 'NA-ECOM', 'Budget', 'Revenue', 0.00, '2026-02-28', 'CC200'),
    (16, 2026, 2, 'NA-ECOM', 'Budget', 'Expense', 660000.00, '2026-02-28', 'CC200'),
    (17, 2026, 1, 'NA-RETAIL', 'Forecast', 'Revenue', 1180000.00, '2026-01-31', 'CC100'),
    (18, 2026, 1, 'NA-RETAIL', 'Actual', 'Other', 50000.00, '2026-01-31', 'CC100'),
    (19, 2026, 1, 'NA-LEGACY', 'Actual', 'Revenue', 450000.00, '2026-01-31', 'CC300'),
    (20, 2026, 1, 'EU-STORE', 'Actual', 'Revenue', 700000.00, '2026-01-31', 'CC400');
