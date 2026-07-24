DECLARE @FiscalYear INT = 2026;
DECLARE @RegionName NVARCHAR(50) = 'North America';

WITH baseline_filtered_postings AS (
    SELECT *
    FROM dbo.FactFinancialPosting
    WHERE FiscalYear = @FiscalYear
),
baseline_actuals AS (
    SELECT
        fp.BusinessUnitCode,
        fp.FiscalMonth,
        SUM(CASE WHEN fp.AccountCategory = 'Revenue' THEN fp.Amount ELSE 0 END) AS ActualRevenue,
        SUM(CASE WHEN fp.AccountCategory = 'Expense' THEN fp.Amount ELSE 0 END) AS ActualExpense
    FROM baseline_filtered_postings fp
    WHERE fp.ScenarioName = 'Actual'
      AND fp.BusinessUnitCode IN (
          SELECT bu.BusinessUnitCode
          FROM dbo.DimBusinessUnit bu
          WHERE bu.IsActive = 1
      )
    GROUP BY fp.BusinessUnitCode, fp.FiscalMonth
),
baseline_budget AS (
    SELECT
        fp.BusinessUnitCode,
        fp.FiscalMonth,
        SUM(CASE WHEN fp.AccountCategory = 'Revenue' THEN fp.Amount ELSE 0 END) AS BudgetRevenue,
        SUM(CASE WHEN fp.AccountCategory = 'Expense' THEN fp.Amount ELSE 0 END) AS BudgetExpense
    FROM baseline_filtered_postings fp
    WHERE fp.ScenarioName = 'Budget'
      AND fp.BusinessUnitCode IN (
          SELECT bu.BusinessUnitCode
          FROM dbo.DimBusinessUnit bu
          WHERE bu.IsActive = 1
      )
    GROUP BY fp.BusinessUnitCode, fp.FiscalMonth
),
baseline_result AS (
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
    FROM baseline_actuals a
    INNER JOIN baseline_budget b
        ON b.BusinessUnitCode = a.BusinessUnitCode
       AND b.FiscalMonth = a.FiscalMonth
    INNER JOIN dbo.DimBusinessUnit bu
        ON bu.BusinessUnitCode = a.BusinessUnitCode
    WHERE bu.RegionName = @RegionName
),
active_business_units AS (
    SELECT
        bu.BusinessUnitCode,
        bu.BusinessUnitName,
        bu.RegionName
    FROM dbo.DimBusinessUnit bu
    WHERE bu.IsActive = 1
      AND bu.RegionName = @RegionName
),
optimized_aggregated_postings AS (
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
),
optimized_result AS (
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
    FROM optimized_aggregated_postings ap
    INNER JOIN active_business_units abu
        ON abu.BusinessUnitCode = ap.BusinessUnitCode
)
SELECT
    'baseline_minus_optimized' AS comparison,
    COUNT(*) AS difference_count
FROM (
    SELECT
        RegionName,
        BusinessUnitCode,
        BusinessUnitName,
        FiscalMonth,
        ActualRevenue,
        ActualExpense,
        BudgetRevenue,
        BudgetExpense,
        RevenueVariance,
        ExpenseVariance,
        RevenueVariancePct,
        ExpenseVariancePct
    FROM baseline_result
    EXCEPT
    SELECT
        RegionName,
        BusinessUnitCode,
        BusinessUnitName,
        FiscalMonth,
        ActualRevenue,
        ActualExpense,
        BudgetRevenue,
        BudgetExpense,
        RevenueVariance,
        ExpenseVariance,
        RevenueVariancePct,
        ExpenseVariancePct
    FROM optimized_result
) baseline_differences
UNION ALL
SELECT
    'optimized_minus_baseline' AS comparison,
    COUNT(*) AS difference_count
FROM (
    SELECT
        RegionName,
        BusinessUnitCode,
        BusinessUnitName,
        FiscalMonth,
        ActualRevenue,
        ActualExpense,
        BudgetRevenue,
        BudgetExpense,
        RevenueVariance,
        ExpenseVariance,
        RevenueVariancePct,
        ExpenseVariancePct
    FROM optimized_result
    EXCEPT
    SELECT
        RegionName,
        BusinessUnitCode,
        BusinessUnitName,
        FiscalMonth,
        ActualRevenue,
        ActualExpense,
        BudgetRevenue,
        BudgetExpense,
        RevenueVariance,
        ExpenseVariance,
        RevenueVariancePct,
        ExpenseVariancePct
    FROM baseline_result
) optimized_differences;
