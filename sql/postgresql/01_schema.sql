-- Run in a NEW qsr_portfolio database. No DROP or destructive resets.

CREATE SCHEMA IF NOT EXISTS qsr;

CREATE TABLE IF NOT EXISTS qsr.stores (
  store_id TEXT NOT NULL,
  store_name TEXT NOT NULL,
  region TEXT NOT NULL,
  has_drive_thru BIGINT NOT NULL,
  treated_store BIGINT NOT NULL,
  PRIMARY KEY (store_id)
);

CREATE TABLE IF NOT EXISTS qsr.items (
  item_id TEXT NOT NULL,
  description TEXT NOT NULL,
  category TEXT NOT NULL,
  base_uom TEXT NOT NULL,
  units_per_case DOUBLE PRECISION NOT NULL,
  unit_cost_gbp DOUBLE PRECISION NOT NULL,
  recipe_units_per_transaction DOUBLE PRECISION NOT NULL,
  PRIMARY KEY (item_id)
);

CREATE TABLE IF NOT EXISTS qsr.sales (
  store_id TEXT NOT NULL,
  date DATE NOT NULL,
  channel TEXT NOT NULL,
  daypart TEXT NOT NULL,
  transactions BIGINT NOT NULL,
  net_sales_gbp DOUBLE PRECISION NOT NULL,
  tax_gbp DOUBLE PRECISION NOT NULL,
  gross_sales_gbp DOUBLE PRECISION NOT NULL,
  PRIMARY KEY (store_id, date, channel, daypart),
  FOREIGN KEY (store_id) REFERENCES qsr.stores(store_id),
  CHECK (ABS(gross_sales_gbp-net_sales_gbp-tax_gbp)<0.011)
);

CREATE TABLE IF NOT EXISTS qsr.employee_shifts (
  shift_id TEXT NOT NULL,
  store_id TEXT NOT NULL,
  date DATE NOT NULL,
  employee_id TEXT NOT NULL,
  role TEXT NOT NULL,
  scheduled_hours DOUBLE PRECISION NOT NULL,
  paid_hours DOUBLE PRECISION NOT NULL,
  absence_flag BIGINT NOT NULL,
  overtime_hours BIGINT NOT NULL,
  hourly_rate_gbp DOUBLE PRECISION NOT NULL,
  wage_cost_gbp DOUBLE PRECISION NOT NULL,
  PRIMARY KEY (shift_id),
  FOREIGN KEY (store_id) REFERENCES qsr.stores(store_id)
);

CREATE TABLE IF NOT EXISTS qsr.service (
  store_id TEXT NOT NULL,
  date DATE NOT NULL,
  daypart TEXT NOT NULL,
  service_orders BIGINT NOT NULL,
  service_total_seconds DOUBLE PRECISION NOT NULL,
  complaints BIGINT NOT NULL,
  PRIMARY KEY (store_id, date, daypart),
  FOREIGN KEY (store_id) REFERENCES qsr.stores(store_id)
);

CREATE TABLE IF NOT EXISTS qsr.delivery (
  store_id TEXT NOT NULL,
  date DATE NOT NULL,
  platform TEXT NOT NULL,
  accepted_orders BIGINT NOT NULL,
  rejected_orders BIGINT NOT NULL,
  offered_orders BIGINT NOT NULL,
  handoff_orders BIGINT NOT NULL,
  handoff_total_seconds DOUBLE PRECISION NOT NULL,
  delivery_accuracy_eligible_orders BIGINT NOT NULL,
  delivery_issue_orders BIGINT NOT NULL,
  scheduled_minutes BIGINT NOT NULL,
  offline_minutes BIGINT NOT NULL,
  PRIMARY KEY (store_id, date, platform),
  FOREIGN KEY (store_id) REFERENCES qsr.stores(store_id)
);

CREATE TABLE IF NOT EXISTS qsr.availability (
  store_id TEXT NOT NULL,
  date DATE NOT NULL,
  daypart TEXT NOT NULL,
  item_id TEXT NOT NULL,
  eligible_minutes BIGINT NOT NULL,
  available_minutes BIGINT NOT NULL,
  gold_checks BIGINT NOT NULL,
  gold_passes BIGINT NOT NULL,
  PRIMARY KEY (store_id, date, daypart, item_id),
  FOREIGN KEY (store_id) REFERENCES qsr.stores(store_id),
  FOREIGN KEY (item_id) REFERENCES qsr.items(item_id)
);

CREATE TABLE IF NOT EXISTS qsr.upgrades (
  store_id TEXT NOT NULL,
  date DATE NOT NULL,
  daypart TEXT NOT NULL,
  upgrade_eligible_transactions BIGINT NOT NULL,
  upgraded_transactions BIGINT NOT NULL,
  incremental_upgrade_sales_gbp DOUBLE PRECISION NOT NULL,
  PRIMARY KEY (store_id, date, daypart),
  FOREIGN KEY (store_id) REFERENCES qsr.stores(store_id)
);

CREATE TABLE IF NOT EXISTS qsr.purchase_orders (
  order_id TEXT NOT NULL,
  line_id BIGINT NOT NULL,
  store_id TEXT NOT NULL,
  item_id TEXT NOT NULL,
  supplier_id TEXT NOT NULL,
  order_date DATE NOT NULL,
  due_date DATE NOT NULL,
  ordered_cases BIGINT NOT NULL,
  case_price_gbp DOUBLE PRECISION NOT NULL,
  PRIMARY KEY (order_id, line_id),
  FOREIGN KEY (store_id) REFERENCES qsr.stores(store_id),
  FOREIGN KEY (item_id) REFERENCES qsr.items(item_id)
);

CREATE TABLE IF NOT EXISTS qsr.receipts (
  receipt_id TEXT NOT NULL,
  order_id TEXT NOT NULL,
  line_id BIGINT NOT NULL,
  store_id TEXT NOT NULL,
  item_id TEXT NOT NULL,
  receipt_date DATE NOT NULL,
  received_cases BIGINT NOT NULL,
  units_per_case DOUBLE PRECISION NOT NULL,
  received_units DOUBLE PRECISION NOT NULL,
  receipt_value_gbp DOUBLE PRECISION NOT NULL,
  PRIMARY KEY (receipt_id),
  FOREIGN KEY (store_id) REFERENCES qsr.stores(store_id),
  FOREIGN KEY (item_id) REFERENCES qsr.items(item_id),
  FOREIGN KEY (order_id,line_id) REFERENCES qsr.purchase_orders(order_id,line_id)
);

CREATE TABLE IF NOT EXISTS qsr.stock (
  store_id TEXT NOT NULL,
  date DATE NOT NULL,
  item_id TEXT NOT NULL,
  opening_units DOUBLE PRECISION NOT NULL,
  received_units DOUBLE PRECISION NOT NULL,
  transfer_in_units DOUBLE PRECISION NOT NULL,
  transfer_out_units DOUBLE PRECISION NOT NULL,
  theoretical_usage_units DOUBLE PRECISION NOT NULL,
  waste_units DOUBLE PRECISION NOT NULL,
  closing_units DOUBLE PRECISION NOT NULL,
  unit_cost_gbp DOUBLE PRECISION NOT NULL,
  PRIMARY KEY (store_id, date, item_id),
  FOREIGN KEY (store_id) REFERENCES qsr.stores(store_id),
  FOREIGN KEY (item_id) REFERENCES qsr.items(item_id)
);

CREATE TABLE IF NOT EXISTS qsr.transfers (
  transfer_id TEXT NOT NULL,
  date DATE NOT NULL,
  from_store_id TEXT NOT NULL,
  to_store_id TEXT NOT NULL,
  item_id TEXT NOT NULL,
  units DOUBLE PRECISION NOT NULL,
  PRIMARY KEY (transfer_id),
  FOREIGN KEY (item_id) REFERENCES qsr.items(item_id)
);

CREATE TABLE IF NOT EXISTS qsr.waste (
  store_id TEXT NOT NULL,
  date DATE NOT NULL,
  item_id TEXT NOT NULL,
  waste_units DOUBLE PRECISION NOT NULL,
  waste_id TEXT NOT NULL,
  reason TEXT NOT NULL,
  PRIMARY KEY (waste_id),
  FOREIGN KEY (store_id) REFERENCES qsr.stores(store_id),
  FOREIGN KEY (item_id) REFERENCES qsr.items(item_id)
);

CREATE TABLE IF NOT EXISTS qsr.stock_counts (
  store_id TEXT NOT NULL,
  date DATE NOT NULL,
  item_id TEXT NOT NULL,
  closing_units DOUBLE PRECISION NOT NULL,
  count_location TEXT NOT NULL,
  PRIMARY KEY (store_id, date, item_id),
  FOREIGN KEY (store_id) REFERENCES qsr.stores(store_id),
  FOREIGN KEY (item_id) REFERENCES qsr.items(item_id)
);

CREATE TABLE IF NOT EXISTS qsr.forecasts (
  store_id TEXT NOT NULL,
  channel TEXT NOT NULL,
  target_date DATE NOT NULL,
  origin_date DATE NOT NULL,
  horizon_days BIGINT NOT NULL,
  model TEXT NOT NULL,
  metric TEXT NOT NULL,
  forecast DOUBLE PRECISION NOT NULL,
  actual DOUBLE PRECISION NOT NULL,
  PRIMARY KEY (store_id, channel, origin_date, target_date, horizon_days, model, metric),
  FOREIGN KEY (store_id) REFERENCES qsr.stores(store_id)
);

CREATE TABLE IF NOT EXISTS qsr.store_daily (
  store_id TEXT NOT NULL,
  date DATE NOT NULL,
  transactions BIGINT NOT NULL,
  net_sales_gbp DOUBLE PRECISION NOT NULL,
  tax_gbp DOUBLE PRECISION NOT NULL,
  gross_sales_gbp DOUBLE PRECISION NOT NULL,
  paid_hours DOUBLE PRECISION NOT NULL,
  scheduled_hours DOUBLE PRECISION NOT NULL,
  wage_cost_gbp DOUBLE PRECISION NOT NULL,
  direct_hours DOUBLE PRECISION NOT NULL,
  manager_hours DOUBLE PRECISION NOT NULL,
  team_wage_cost_gbp DOUBLE PRECISION NOT NULL,
  overtime_hours BIGINT NOT NULL,
  absence_flag BIGINT NOT NULL,
  food_cost_gbp DOUBLE PRECISION NOT NULL,
  packaging_cost_gbp DOUBLE PRECISION NOT NULL,
  waste_cost_gbp DOUBLE PRECISION NOT NULL,
  service_orders BIGINT NOT NULL,
  service_total_seconds DOUBLE PRECISION NOT NULL,
  complaints BIGINT NOT NULL,
  accepted_orders BIGINT NOT NULL,
  offered_orders BIGINT NOT NULL,
  rejected_orders BIGINT NOT NULL,
  handoff_orders BIGINT NOT NULL,
  handoff_total_seconds DOUBLE PRECISION NOT NULL,
  delivery_accuracy_eligible_orders BIGINT NOT NULL,
  delivery_issue_orders BIGINT NOT NULL,
  offline_minutes BIGINT NOT NULL,
  scheduled_minutes BIGINT NOT NULL,
  eligible_minutes BIGINT NOT NULL,
  available_minutes BIGINT NOT NULL,
  gold_checks BIGINT NOT NULL,
  gold_passes BIGINT NOT NULL,
  upgrade_eligible_transactions BIGINT NOT NULL,
  upgraded_transactions BIGINT NOT NULL,
  incremental_upgrade_sales_gbp DOUBLE PRECISION NOT NULL,
  delivery_net_sales_gbp DOUBLE PRECISION NOT NULL,
  store_name TEXT NOT NULL,
  region TEXT NOT NULL,
  has_drive_thru BIGINT NOT NULL,
  treated_store BIGINT NOT NULL,
  post_period BIGINT NOT NULL,
  forecast_sales_gbp DOUBLE PRECISION,
  PRIMARY KEY (store_id, date),
  FOREIGN KEY (store_id) REFERENCES qsr.stores(store_id)
);
