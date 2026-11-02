# Data dictionary (v0.2)

All exported rows are fictional. Field names are canonical portfolio mappings, not asserted source
export headers. Amounts are GBP; net sales exclude tax; percentages in Python are 0–100, DAX rates
are 0–1. All identifiers are strings, dates ISO calendar dates, counts integers, hours/units/amounts
numeric. Null means unavailable, never measured zero. Primary keys must be nonnull and unique.

| Table | Grain / key | Fields and meaning |
|---|---|---|
| stores | store_id | store_name, region fictional labels; has_drive_thru and treated_store binary |
| items | item_id | description/category (food or packaging), base_uom (kg/each), units_per_case, unit_cost_gbp fixed synthetic standard cost, recipe_units_per_transaction fictional usage coefficient |
| sales | store_id,date,channel,daypart | transactions completed orders; net_sales_gbp ex-tax; tax_gbp; gross_sales_gbp = net + tax. Channel eat_in/takeout/drive_thru/delivery; five mutually exclusive dayparts |
| employee_shifts | shift_id | store_id,date,employee_id fictional; role team/manager; scheduled_hours, paid_hours, absence_flag (absent -> zero paid), overtime_hours above fictional 8h threshold, hourly_rate_gbp, wage_cost_gbp = paid × rate rounded to pennies. Paid hours exclude unpaid breaks by assumption |
| service | store_id,date,daypart | service_orders denominator; service_total_seconds sum; complaints count. All-orders demo timer, not official FC pack/OTD |
| delivery | store_id,date,platform | accepted_orders, rejected_orders, offered_orders = accepted + rejected; handoff_orders, handoff_total_seconds; delivery_accuracy_eligible_orders, delivery_issue_orders; scheduled_minutes and offline_minutes per platform, not unique restaurant clock minutes |
| availability | store_id,date,daypart,item_id | eligible_minutes, available_minutes; gold_checks, gold_passes. Fictional time/check proxies, not confirmed source definitions |
| upgrades | store_id,date,daypart | upgrade_eligible_transactions, upgraded_transactions subset; incremental_upgrade_sales_gbp fictional incremental revenue, already contained in sales (not added again) |
| purchase_orders | order_id,line_id | store_id,item_id,supplier_id fictional; order_date,due_date; ordered_cases; case_price_gbp commitment price, not stock usage |
| receipts | receipt_id | order_id,line_id FK; store_id,item_id; receipt_date; received_cases, units_per_case, received_units; receipt_value_gbp. Repeated PO line receipts allowed |
| stock_counts | store_id,date,item_id | closing_units counted at fictional day end; count_location is all_locations_consolidated |
| waste | waste_id | store_id,date,item_id,waste_units in base UOM; reason fictional_spoilage |
| transfers | transfer_id | date,from_store_id,to_store_id,item_id,units; one event produces equal outbound/inbound ledger entries |
| stock | store_id,date,item_id | opening_units,received_units,transfer_in_units,transfer_out_units,theoretical_usage_units,waste_units,closing_units,unit_cost_gbp; generated count-period balance, not a confirmed stock export |
| forecasts | store_id,channel,origin_date,target_date,horizon_days,model,metric | forecast and actual; model seasonal_naive or weekday_mean_4; metric net_sales_gbp or transactions. Seven-day horizon, 28-day minimum history; actual used only for scoring |
| store_daily | store_id,date | Validated aggregate mart below. Warm-up forecast_sales_gbp is null until a forecast is issued |

## Store-day mart and engineered measures

Additive primitives: transactions, gross_sales_gbp, net_sales_gbp, tax_gbp; scheduled_hours,
paid_hours, direct_hours (team paid), manager_hours, overtime_hours; wage_cost_gbp,
team_wage_cost_gbp, absence_flag (number of absent shifts); food_cost_gbp (actual food usage,
**including waste**), packaging_cost_gbp, waste_cost_gbp (food only); complaints; service_orders,
service_total_seconds; accepted_orders,offered_orders,rejected_orders,handoff_orders,
handoff_total_seconds,delivery_accuracy_eligible_orders,delivery_issue_orders,scheduled_minutes,
offline_minutes; eligible_minutes,available_minutes,gold_checks,gold_passes;
upgrade_eligible_transactions,upgraded_transactions,incremental_upgrade_sales_gbp;
delivery_net_sales_gbp. forecast_sales_gbp is a selected seasonal-naive sales vintage, not a
budget or screenshot-derived forecast. Descriptors: store_name,region,has_drive_thru,
treated_store,post_period (fictional common launch on 2026-03-02).

| Derived measure | Formula / interpretation |
|---|---|
| revenue_ex_vat_gbp | net_sales_gbp, retained compatibility alias; no divide by 1.2 |
| avg_transaction_value_gbp | net / transactions |
| transactions_per_paid_hour | transactions / all paid hours |
| direct_transactions_per_hour | transactions / team paid hours; candidate DTPLH mapping, unconfirmed |
| sales_per_paid_hour_gbp | net / all paid hours |
| labour_cost_pct | 100 × all wages / net |
| team_labour_cost_pct | 100 × team wages / net; distinct from total labour % |
| food_cost_pct, waste_pct_sales | 100 × respective food cost / net |
| gross_profit_gbp | net - food usage; partial gross margin before packaging and other costs |
| contribution_profit_gbp | net - food usage - packaging usage - wages; excludes rent, fees, utilities etc., not EBITDA |
| complaints_per_1000_orders | 1000 × complaints / transactions |
| avg_service_seconds, driver_handoff_seconds | sum elapsed seconds / measured orders; distinct timer populations |
| delivery_sales_mix_pct | 100 × delivery net / all net; not order share |
| delivery_issue_pct | 100 × issue orders / eligible orders; adverse fictional metric |
| rejection_pct, offline_pct | 100 × rejected/offered, 100 × offline/scheduled platform minutes |
| upgrade_rate_pct | 100 × upgraded / eligible transactions |
| availability_pct | 100 × available / eligible item-minutes |
| forecast_error_gbp | actual - forecast (positive = underforecast) |
| absolute_percentage_error_pct | 100 × abs(actual - forecast) / actual; undefined for actual zero |

For period KPIs recompute ratios from summed additive numerators/denominators. Do not average
ATV, percentages, daypart means or platform ratings. Aggregate forecast WAPE sums absolute
errors **before** aggregation; netting positive and negative errors is not WAPE. Positive
forecast-score bias means overforecast (forecast - actual), opposite to daily error's sign.
Historical reports containing pre-v0.2 net sales must be regenerated: their field meaning changed.

## Proposed, unavailable source contracts

Raw sales lines, discounts/refunds, transaction timestamps, recipes/yields, actual shift intervals,
forecast revisions, scorecard rule tables and LY/fiscal date mappings await authorized exports.
Recommended snapshot key: store_id,report_id,period_start,period_end,window,metric_id,coverage,
extract_timestamp,rule_version; values include numeric_value,unit,source_status. Do not infer
missing snapshots, scoring thresholds, or official overall scores from this demo.
