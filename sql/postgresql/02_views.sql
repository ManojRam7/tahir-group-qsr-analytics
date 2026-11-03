-- Additive daily primitives plus correctly defined measures. No fact-to-fact fan-out.
CREATE OR REPLACE VIEW qsr.v_daily_kpis AS
SELECT d.*,
 net_sales_gbp/NULLIF(transactions,0) AS average_ticket_gbp,
 transactions/NULLIF(paid_hours,0) AS transactions_per_paid_hour,
 transactions/NULLIF(direct_hours,0) AS direct_transactions_per_hour,
 net_sales_gbp/NULLIF(paid_hours,0) AS sales_per_paid_hour,
 100*wage_cost_gbp/NULLIF(net_sales_gbp,0) AS labour_cost_pct,
 100*team_wage_cost_gbp/NULLIF(net_sales_gbp,0) AS team_labour_cost_pct,
 100*waste_cost_gbp/NULLIF(net_sales_gbp,0) AS food_waste_pct,
 net_sales_gbp-food_cost_gbp-packaging_cost_gbp-wage_cost_gbp AS contribution_gbp,
 handoff_total_seconds/NULLIF(handoff_orders,0) AS handoff_seconds
FROM qsr.store_daily d;

CREATE OR REPLACE VIEW qsr.v_inventory_balance AS
SELECT *, opening_units+received_units+transfer_in_units-transfer_out_units-closing_units AS actual_usage_units,
 opening_units+received_units+transfer_in_units-transfer_out_units-closing_units-theoretical_usage_units-waste_units AS unexplained_units
FROM qsr.stock;

CREATE OR REPLACE VIEW qsr.v_forecast_scores AS
SELECT model,metric,horizon_days,COUNT(*) AS observations,
 AVG(ABS(forecast-actual)) AS mae,
 SQRT(AVG(POWER(forecast-actual,2))) AS rmse,
 100*SUM(ABS(forecast-actual))/NULLIF(SUM(actual),0) AS wape_pct,
 100*SUM(forecast-actual)/NULLIF(SUM(actual),0) AS bias_pct
FROM qsr.forecasts GROUP BY model,metric,horizon_days;

CREATE OR REPLACE VIEW qsr.dim_date AS
SELECT DISTINCT date, DATE_TRUNC('week',date)::date AS week_start,
 EXTRACT(ISODOW FROM date) AS weekday_number,
 EXTRACT(MONTH FROM date) AS month_number
FROM qsr.store_daily;

CREATE OR REPLACE VIEW qsr.v_store_week AS
SELECT store_id,DATE_TRUNC('week',date)::date AS week_start,COUNT(*) AS days_loaded,
 SUM(net_sales_gbp) AS net_sales_gbp,SUM(transactions) AS transactions,
 SUM(paid_hours) AS paid_hours,SUM(wage_cost_gbp) AS wage_cost_gbp,
 SUM(transactions)/NULLIF(SUM(paid_hours),0) AS transactions_per_paid_hour,
 100*SUM(wage_cost_gbp)/NULLIF(SUM(net_sales_gbp),0) AS labour_cost_pct
FROM qsr.store_daily GROUP BY store_id,DATE_TRUNC('week',date)::date;
