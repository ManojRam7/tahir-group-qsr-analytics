-- 1. Is the imported dataset complete? Expected: 12 stores, 112 dates, 1344 rows.
SELECT COUNT(*) AS store_days, COUNT(DISTINCT store_id) AS stores,
 COUNT(DISTINCT date) AS dates, MIN(date) AS first_date, MAX(date) AS last_date,
 SUM(gross_sales_gbp)-SUM(net_sales_gbp)-SUM(tax_gbp) AS tax_reconciliation
FROM qsr.store_daily;

-- 2. Which stores need a labour conversation? High cost is a prompt, not proof of inefficiency.
SELECT store_id,SUM(net_sales_gbp) AS sales,SUM(wage_cost_gbp) AS wages,
 100*SUM(wage_cost_gbp)/NULLIF(SUM(net_sales_gbp),0) AS labour_pct,
 SUM(transactions)/NULLIF(SUM(paid_hours),0) AS orders_per_paid_hour
FROM qsr.store_daily GROUP BY store_id ORDER BY labour_pct DESC;

-- 3. Compare complete consecutive weeks; exclude partial weeks.
WITH complete AS (SELECT * FROM qsr.v_store_week WHERE days_loaded=7), compared AS (
 SELECT *,LAG(net_sales_gbp) OVER(PARTITION BY store_id ORDER BY week_start) AS previous_sales,
 LAG(week_start) OVER(PARTITION BY store_id ORDER BY week_start) AS previous_week FROM complete)
SELECT *,100*(net_sales_gbp-previous_sales)/NULLIF(previous_sales,0) AS sales_change_pct
FROM compared WHERE week_start=previous_week+7 ORDER BY store_id,week_start;

-- 4. Which items have unexplained usage? Keep units and standard cost separate from invoice cost.
SELECT store_id,item_id,SUM(unexplained_units) AS unexplained_units,
 SUM(unexplained_units*unit_cost_gbp) AS unexplained_standard_cost_gbp
FROM qsr.v_inventory_balance GROUP BY store_id,item_id ORDER BY unexplained_standard_cost_gbp DESC;

-- 5. Ordered versus received cases; receipt lines aggregate BEFORE joining PO lines.
WITH r AS (SELECT order_id,line_id,SUM(received_cases) AS received_cases FROM qsr.receipts GROUP BY order_id,line_id)
SELECT p.order_id,p.store_id,p.item_id,p.ordered_cases,COALESCE(r.received_cases,0) AS received_cases,
 p.ordered_cases-COALESCE(r.received_cases,0) AS outstanding_cases
FROM qsr.purchase_orders p LEFT JOIN r USING(order_id,line_id)
WHERE p.ordered_cases>COALESCE(r.received_cases,0);

-- 6. Delivery timer and adverse issue rate use their own eligible populations.
SELECT store_id,platform,SUM(handoff_total_seconds)/NULLIF(SUM(handoff_orders),0) AS handoff_seconds,
 100.0*SUM(delivery_issue_orders)/NULLIF(SUM(delivery_accuracy_eligible_orders),0) AS issue_pct
FROM qsr.delivery GROUP BY store_id,platform;

-- 7. Manual DID uses equal store-day means, unlike the portfolio ratio-of-sums.
WITH m AS (SELECT treated_store,post_period,AVG(transactions_per_paid_hour) AS y
FROM qsr.v_daily_kpis GROUP BY treated_store,post_period)
SELECT SUM(CASE WHEN treated_store=post_period THEN y ELSE -y END) AS did_orders_per_paid_hour FROM m;
-- Formula: treated post - treated pre - control post + control pre. Inference is in Python.
