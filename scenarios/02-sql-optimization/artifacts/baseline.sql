DECLARE @FiscalYear INT = 2026;
DECLARE @RegionName NVARCHAR(50) = 'North America';

WITH filtered_postings AS (
    SELECT *
    FROM dbo.FactFinancialPosting
    WHERE FiscalYear = @FiscalYear
),
actuals AS (
    SELECT
        fp.BusinessUnitCode,
        fp.FiscalMonth,
        SUM(CASE WHEN fp.AccountCategory = 'Revenue' THEN fp.Amount ELSE 0 END) AS ActualRevenue,
        SUM(CASE WHEN fp.AccountCategory = 'Expense' THEN fp.Amount ELSE 0 END) AS ActualExpense
    FROM filtered_postings fp
    WHERE fp.ScenarioName = 'Actual'
      AND fp.BusinessUnitCode IN (
          SELECT bu.BusinessUnitCode
          FROM dbo.DimBusinessUnit bu
          WHERE bu.IsActive = 1
      )
    GROUP BY fp.BusinessUnitCode, fp.FiscalMonth
),
budget AS (
    SELECT
        fp.BusinessUnitCode,
        fp.FiscalMonth,
        SUM(CASE WHEN fp.AccountCategory = 'Revenue' THEN fp.Amount ELSE 0 END) AS BudgetRevenue,
        SUM(CASE WHEN fp.AccountCategory = 'Expense' THEN fp.Amount ELSE 0 END) AS BudgetExpense
    FROM filtered_postings fp
    WHERE fp.ScenarioName = 'Budget'
      AND fp.BusinessUnitCode IN (
          SELECT bu.BusinessUnitCode
          FROM dbo.DimBusinessUnit bu
          WHERE bu.IsActive = 1
      )
    GROUP BY fp.BusinessUnitCode, fp.FiscalMonth
),
joined_results AS (
    SELECT
        bu.RegionName,
        a.BusinessUnitCode,
        bu.BusinessUnitName,
        a.FiscalMonth,
        a.ActualRevenue,
        a.ActualExpense,
        b.BudgetRevenue,
        b.BudgetExpense,
        a.ActualRevenue - b.BudgetRevenue AS RevenueVariance,
        a.ActualExpense - b.BudgetExpense AS ExpenseVariance,
        CASE
            WHEN b.BudgetRevenue = 0 THEN NULL
            ELSE CAST(a.ActualRevenue - b.BudgetRevenue AS DECIMAL(19, 4)) / CAST(b.BudgetRevenue AS DECIMAL(19, 4))
        END AS RevenueVariancePct,
        CASE
            WHEN b.BudgetExpense = 0 THEN NULL
            ELSE CAST(a.ActualExpense - b.BudgetExpense AS DECIMAL(19, 4)) / CAST(b.BudgetExpense AS DECIMAL(19, 4))
        END AS ExpenseVariancePct
    FROM actuals a
    INNER JOIN budget b
        ON b.BusinessUnitCode = a.BusinessUnitCode
       AND b.FiscalMonth = a.FiscalMonth
    INNER JOIN dbo.DimBusinessUnit bu
        ON bu.BusinessUnitCode = a.BusinessUnitCode
)
SELECT *
FROM joined_results
WHERE RegionName = @RegionName
ORDER BY BusinessUnitCode, FiscalMonth;
