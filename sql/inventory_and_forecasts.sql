-- Actual usage includes recorded waste. Positive unexplained usage means additional loss.
SELECT store_id, date, item_id,
    opening_units+received_units+transfer_in_units-transfer_out_units-closing_units AS actual_usage_units,
    opening_units+received_units+transfer_in_units-transfer_out_units-closing_units
        -theoretical_usage_units-waste_units AS unexplained_units,
    (opening_units+received_units+transfer_in_units-transfer_out_units-closing_units)
        *unit_cost_gbp AS usage_cost_gbp
FROM stock;

-- Each model/metric/horizon evaluated on its issued forecasts. No signed-error cancellation.
SELECT model, metric, horizon_days, COUNT(*) AS n,
    AVG(ABS(forecast-actual)) AS mae,
    SQRT(AVG(POWER(forecast-actual,2))) AS rmse,
    100.0 * SUM(ABS(forecast-actual))/NULLIF(SUM(actual),0) AS wape_pct,
    100.0 * SUM(forecast-actual)/NULLIF(SUM(actual),0) AS bias_pct
FROM forecasts GROUP BY model,metric,horizon_days;
