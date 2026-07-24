DECLARE @FiscalYear INT = 2026;
DECLARE @RegionName NVARCHAR(50) = 'North America';

WITH active_business_units AS (
    SELECT
        bu.BusinessUnitCode,
        bu.BusinessUnitName,
        bu.RegionName
    FROM dbo.DimBusinessUnit bu
    WHERE bu.IsActive = 1
      AND bu.RegionName = @RegionName
),
aggregated_postings AS (
    SELECT
        fp.BusinessUnitCode,
        fp.FiscalMonth,
        SUM(CASE WHEN fp.ScenarioName = 'Actual' AND fp.AccountCategory = 'Revenue' THEN fp.Amount ELSE 0 END) AS ActualRevenue,
        SUM(CASE WHEN fp.ScenarioName = 'Actual' AND fp.AccountCategory = 'Expense' THEN fp.Amount ELSE 0 END) AS ActualExpense,
        SUM(CASE WHEN fp.ScenarioName = 'Budget' AND fp.AccountCategory = 'Revenue' THEN fp.Amount ELSE 0 END) AS BudgetRevenue,
        SUM(CASE WHEN fp.ScenarioName = 'Budget' AND fp.AccountCategory = 'Expense' THEN fp.Amount ELSE 0 END) AS BudgetExpense
    FROM dbo.FactFinancialPosting fp
    INNER JOIN active_business_units abu
        ON abu.BusinessUnitCode = fp.BusinessUnitCode
    WHERE fp.FiscalYear = @FiscalYear
      AND fp.ScenarioName IN ('Actual', 'Budget')
      AND fp.AccountCategory IN ('Revenue', 'Expense')
    GROUP BY
        fp.BusinessUnitCode,
        fp.FiscalMonth
)
SELECT
    abu.RegionName,
    ap.BusinessUnitCode,
    abu.BusinessUnitName,
    ap.FiscalMonth,
    ap.ActualRevenue,
    ap.ActualExpense,
    ap.BudgetRevenue,
    ap.BudgetExpense,
    ap.ActualRevenue - ap.BudgetRevenue AS RevenueVariance,
    ap.ActualExpense - ap.BudgetExpense AS ExpenseVariance,
    CAST(ap.ActualRevenue - ap.BudgetRevenue AS DECIMAL(19, 4)) / NULLIF(CAST(ap.BudgetRevenue AS DECIMAL(19, 4)), 0) AS RevenueVariancePct,
    CAST(ap.ActualExpense - ap.BudgetExpense AS DECIMAL(19, 4)) / NULLIF(CAST(ap.BudgetExpense AS DECIMAL(19, 4)), 0) AS ExpenseVariancePct
FROM aggregated_postings ap
INNER JOIN active_business_units abu
    ON abu.BusinessUnitCode = ap.BusinessUnitCode
ORDER BY
    ap.BusinessUnitCode,
    ap.FiscalMonth;
