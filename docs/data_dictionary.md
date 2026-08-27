# Data Dictionary

## `store_daily`

Grain: **one row per store per date**.

| Variable | Type | Meaning |
|---|---|---|
| `date` | date | Trading date |
| `store_id` | text | Synthetic store identifier |
| `store_name` | text | Synthetic store name |
| `region` | text | Operating region |
| `treated_store` | int | 1 if store belongs to intervention group |
| `post_period` | int | 1 on/after intervention date |
| `transactions` | int | Completed orders/transactions |
| `net_sales_gbp` | decimal | Gross customer sales incl. VAT in synthetic example |
| `forecast_sales_gbp` | decimal | Pre-period sales forecast used for forecast-error analysis |
| `paid_hours` | decimal | Paid labour hours for the store/day |
| `wage_cost_gbp` | decimal | Direct wage cost |
| `food_cost_gbp` | decimal | Ingredient/food usage cost |
| `waste_cost_gbp` | decimal | Cost value of recorded waste |
| `avg_service_seconds` | decimal | Mean service/fulfilment time |
| `complaints` | int | Count of customer complaints |
| `promo_flag` | int | 1 if promotion active |
| `delivery_mix_pct` | decimal | Delivery share of transactions/sales proxy |
| `weather_index` | decimal | Synthetic standardised weather-demand control |
| `local_event_flag` | int | 1 if a local demand event occurred |

### Engineered variables

| Variable | Formula |
|---|---|
| `revenue_ex_vat_gbp` | `net_sales_gbp / 1.20` |
| `avg_transaction_value_gbp` | `net_sales_gbp / transactions` |
| `transactions_per_paid_hour` | `transactions / paid_hours` |
| `sales_per_paid_hour_gbp` | `net_sales_gbp / paid_hours` |
| `labour_cost_pct` | `wage_cost_gbp / revenue_ex_vat_gbp * 100` |
| `food_cost_pct` | `food_cost_gbp / revenue_ex_vat_gbp * 100` |
| `waste_pct_sales` | `waste_cost_gbp / revenue_ex_vat_gbp * 100` |
| `complaints_per_1000_orders` | `complaints / transactions * 1000` |
| `forecast_error_gbp` | `net_sales_gbp - forecast_sales_gbp` |
| `absolute_percentage_error_pct` | `abs(forecast_error_gbp / net_sales_gbp) * 100` |
| `gross_profit_gbp` | `revenue_ex_vat_gbp - food_cost_gbp` |
| `contribution_profit_gbp` | `revenue_ex_vat_gbp - food_cost_gbp - wage_cost_gbp - waste_cost_gbp` |

## `employee_shifts`

Grain: **one row per employee shift**.

| Variable | Type | Meaning |
|---|---|---|
| `shift_id` | text | Synthetic unique shift ID |
| `date` | date | Shift date |
| `store_id` | text | Store worked |
| `employee_id` | text | Synthetic employee identifier |
| `role` | text | Team Member, Cook or Shift Manager |
| `scheduled_hours` | decimal | Planned shift hours |
| `paid_hours` | decimal | Actual paid hours |
| `absence_flag` | int | Synthetic absence indicator |
| `overtime_hours` | decimal | Hours above the defined daily threshold |

## Recommended additional real-world source tables

A production restaurant analytics environment could also contain:

- transaction-line POS data: product, quantity, price, discounts, tender, order channel, hour/daypart;
- product/menu master: category, recipe, standard cost, launch/discontinue dates;
- inventory movements: opening stock, deliveries, transfers, usage, waste, closing stock;
- labour schedules and clock-in/clock-out records;
- employee master: role, contracted hours, tenure, store/home location;
- service-system timestamps: order placed, kitchen start, ready, handoff;
- customer feedback/complaint categories;
- store targets and budgets;
- promotion calendar;
- local holidays/events/weather data.

These tables should be modelled at their native grain and aggregated deliberately before cross-fact joins.
