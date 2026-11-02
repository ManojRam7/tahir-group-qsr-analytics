-- PostgreSQL / DuckDB compatible. store_daily is already one validated row/store/date.
-- Aggregate primitives first. All percentages here use 0..100; zero denominators yield NULL.
SELECT store_id,
    SUM(net_sales_gbp) AS net_sales_gbp,
    SUM(gross_sales_gbp) AS gross_sales_gbp,
    SUM(tax_gbp) AS tax_gbp,
    SUM(net_sales_gbp) / NULLIF(SUM(transactions),0) AS avg_transaction_value_gbp,
    1.0 * SUM(transactions) / NULLIF(SUM(paid_hours),0) AS transactions_per_paid_hour,
    1.0 * SUM(transactions) / NULLIF(SUM(direct_hours),0) AS direct_transactions_per_hour,
    100.0 * SUM(wage_cost_gbp) / NULLIF(SUM(net_sales_gbp),0) AS labour_cost_pct,
    100.0 * SUM(team_wage_cost_gbp) / NULLIF(SUM(net_sales_gbp),0) AS team_labour_cost_pct,
    100.0 * SUM(food_cost_gbp) / NULLIF(SUM(net_sales_gbp),0) AS food_cost_pct,
    100.0 * SUM(waste_cost_gbp) / NULLIF(SUM(net_sales_gbp),0) AS waste_pct_sales,
    SUM(net_sales_gbp-food_cost_gbp-packaging_cost_gbp-wage_cost_gbp) AS contribution_profit_gbp,
    SUM(service_total_seconds) / NULLIF(SUM(service_orders),0) AS avg_service_seconds,
    SUM(handoff_total_seconds) / NULLIF(SUM(handoff_orders),0) AS driver_handoff_seconds,
    100.0 * SUM(delivery_net_sales_gbp) / NULLIF(SUM(net_sales_gbp),0) AS delivery_sales_mix_pct,
    100.0 * SUM(rejected_orders) / NULLIF(SUM(offered_orders),0) AS rejection_pct,
    100.0 * SUM(offline_minutes) / NULLIF(SUM(scheduled_minutes),0) AS offline_pct,
    100.0 * SUM(delivery_issue_orders) / NULLIF(SUM(delivery_accuracy_eligible_orders),0) AS delivery_issue_pct,
    100.0 * SUM(upgraded_transactions) / NULLIF(SUM(upgrade_eligible_transactions),0) AS upgrade_rate_pct,
    100.0 * SUM(available_minutes) / NULLIF(SUM(eligible_minutes),0) AS availability_pct,
    1000.0 * SUM(complaints) / NULLIF(SUM(transactions),0) AS complaints_per_1000_orders
FROM store_daily GROUP BY store_id;
