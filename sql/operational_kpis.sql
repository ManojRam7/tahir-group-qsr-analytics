-- PostgreSQL example: store/day operational KPIs
-- Grain must remain one row per store_id + date before joining to shift-level tables.

WITH daily AS (
    SELECT
        date,
        store_id,
        net_sales_gbp,
        net_sales_gbp / 1.20 AS revenue_ex_vat_gbp,
        transactions,
        paid_hours,
        wage_cost_gbp,
        food_cost_gbp,
        waste_cost_gbp,
        complaints,
        forecast_sales_gbp
    FROM store_daily
)
SELECT
    date,
    store_id,
    net_sales_gbp,
    revenue_ex_vat_gbp,
    transactions,
    net_sales_gbp / NULLIF(transactions, 0) AS avg_transaction_value_gbp,
    transactions / NULLIF(paid_hours, 0) AS transactions_per_paid_hour,
    net_sales_gbp / NULLIF(paid_hours, 0) AS sales_per_paid_hour_gbp,
    100.0 * wage_cost_gbp / NULLIF(revenue_ex_vat_gbp, 0) AS labour_cost_pct,
    100.0 * food_cost_gbp / NULLIF(revenue_ex_vat_gbp, 0) AS food_cost_pct,
    100.0 * waste_cost_gbp / NULLIF(revenue_ex_vat_gbp, 0) AS waste_pct_sales,
    1000.0 * complaints / NULLIF(transactions, 0) AS complaints_per_1000_orders,
    100.0 * ABS(net_sales_gbp - forecast_sales_gbp) / NULLIF(net_sales_gbp, 0) AS ape_pct,
    revenue_ex_vat_gbp - food_cost_gbp - wage_cost_gbp - waste_cost_gbp AS contribution_profit_gbp
FROM daily;

-- Correct way to join shift data: aggregate first, then join.
WITH shift_daily AS (
    SELECT
        date,
        store_id,
        SUM(paid_hours) AS shift_paid_hours,
        SUM(overtime_hours) AS overtime_hours,
        SUM(absence_flag) AS absence_shifts
    FROM employee_shifts
    GROUP BY 1, 2
)
SELECT d.*, s.shift_paid_hours, s.overtime_hours, s.absence_shifts
FROM store_daily d
LEFT JOIN shift_daily s
  ON d.date = s.date
 AND d.store_id = s.store_id;
