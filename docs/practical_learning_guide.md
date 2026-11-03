# QSR analytics practical learning guide

Business questions to PostgreSQL queries and Power BI reports

## What you will build

You will load the existing fictional restaurant data into PostgreSQL, query it using pgAdmin, create reusable KPI views and build five Power BI report pages. The web portfolio dashboard demonstrates the intended views now. It is a web app, not a PBIX file.

Verified project scope: 12 fictional stores, 112 dates from 5 January to 26 April 2026, 1,344 store-day rows, 26,880 channel/daypart sales rows and 16 tables. The repository has tested calculations and a notebook. No private source images or real restaurant figures are needed.

## Agree the business questions first

Sales: which stores or channels explain the movement in revenue and transactions?

Labour: is paid time aligned with demand, and are team and management costs understood?

Inventory: what was ordered, received, counted, wasted or transferred?

Forecasting: how wrong were forecasts that genuinely existed before the trading date?

Intervention: did treated stores change more than comparable stores over the same dates?

## Use an explicit evidence boundary

The source screenshots support broad reporting structures, but do not reveal all internal definitions. The cadence, intended audiences, synthetic costs, recipe coefficients, stock policy and staffing target here are learning assumptions. Do not describe them as Tahir Group policy. An accurate replica needs authorised exports and signed-off definitions.

Proposed audience: restaurant managers, area managers and finance. Proposed cadence: previous-day reconciliation each morning, a weekly demand/rota review and a monthly review. This is a realistic operating design, not a verified history of report use.

Learning files: sql/postgresql/01_schema.sql; 02_views.sql; 03_business_questions.sql; import_manifest.csv; powerbi/measures.dax; and the 16 generated CSVs. The accompanying ZIP places these in clearly named folders.

## 1 Set up the database and desktop interface

PostgreSQL is the database server that stores rows. pgAdmin is the desktop application used to connect to the server and run SQL. They are different parts of the setup.

Install PostgreSQL from the official macOS download page. The EDB installer includes PostgreSQL and pgAdmin. Save your own database password securely; do not put it in source files.

Open pgAdmin. Under Servers, register a server if none is listed: name QSR Local, host localhost, port 5432, maintenance database postgres, username postgres and your installation password. These defaults apply when the server is on the same Mac.

Right-click Databases, choose Create > Database, and name it qsr_portfolio. Select that database before opening Tools > Query Tool.

Open 01_schema.sql in Query Tool and execute it. Refresh Schemas > qsr > Tables. You should see 16 empty tables. The script has no DROP commands. Use a new empty database for this exercise.

## Generate data if you are using the repository

python scripts/generate_synthetic_data.py

python scripts/run_analysis.py

python scripts/prepare_psql_import.py

Run these from the repository root in the prepared Python environment. If you use the supplied learning ZIP, its data folder already contains the generated CSVs. Generated rows are deterministic for seed 42.

## Understand the keys before importing

stores is one row per store. items is one row per stock item. sales is store/date/channel/daypart. employee_shifts is one row per shift. purchase_orders is order/line. receipts is receipt ID and can reference the same order line more than once. store_daily is one row per store/date.

The schema includes primary and foreign keys. Load parent tables before child tables. A duplicate-key error is useful: it prevents an accidental second load from silently doubling the dataset.

## 2 Import and reconcile the data

## Manual pgAdmin import

Import in this order: stores, items, sales, employee_shifts, service, delivery, availability, upgrades, purchase_orders, receipts, stock, transfers, waste, stock_counts, forecasts, store_daily.

Right-click each table > Import/Export Data. Choose Import, the matching CSV file, Format CSV, Encoding UTF8, Header Yes and delimiter comma. Check that the Columns tab follows import_manifest.csv.

Leave conversion errors set to stop. Run the import, inspect Process Watcher/Messages and refresh the table. Blank forecast_sales_gbp during warm-up is NULL, not zero.

Compare the imported row count with import_manifest.csv. Do not import the same file twice. For a fresh repeat, use a separate practice database or explicitly clear only your exercise tables.

## Repeatable psql alternative

The generated output/postgresql/import_local.psql contains local paths and a transaction. It belongs on your own machine and is intentionally not committed. Run this in a terminal with psql installed:

psql -h localhost -U postgres -d qsr_portfolio \

  -f output/postgresql/import_local.psql

The backslash-copy command is a psql client command. Do not paste it into pgAdmin Query Tool. pgAdmin uses its import dialog; server-side COPY may require server filesystem permissions.

## Your first reconciliation query

SELECT COUNT(*) AS rows, COUNT(DISTINCT store_id) AS stores,

 COUNT(DISTINCT date) AS days,

 SUM(gross_sales_gbp)-SUM(net_sales_gbp)-SUM(tax_gbp) AS gap

FROM qsr.store_daily;

Expected: 1,344 rows, 12 stores, 112 days and a tax gap near zero within floating-point tolerance. There are 26,880 rows in sales. Check MIN(date) and MAX(date) before interpreting a report.

For missing rows or an error, stop the report refresh and inspect the specific file, date, key and data type. Do not replace unknown values with zero to make the dashboard look complete.

## 3 Create and explain the KPI views

Open and execute 02_views.sql in Query Tool. Views save query logic; they do not create a separate manually maintained copy of the data. Use SELECT * FROM qsr.v_daily_kpis LIMIT 10 to inspect results.

## Core definitions

Net sales already excludes tax. Gross = net + reported tax; never divide net by 1.2 again.

Average ticket = SUM(net sales) / SUM(transactions).

Total labour % = 100 × SUM(all wages) / SUM(net sales). Team labour uses team wages only.

Sales per paid hour = SUM(net sales) / SUM(paid hours). Direct productivity uses team hours; all-paid productivity includes management.

Food usage includes recorded waste. Partial contribution = net sales - food usage - packaging usage - wages. It is not EBITDA.

Service mean = total measured seconds / measured orders. Different timers and channel populations cannot be mixed.

## A query you should be able to write from memory

SELECT store_id, SUM(net_sales_gbp) AS sales,

 100*SUM(wage_cost_gbp)/NULLIF(SUM(net_sales_gbp),0) AS labour_pct,

 SUM(transactions)/NULLIF(SUM(paid_hours),0) AS orders_per_hour

FROM qsr.store_daily

GROUP BY store_id

ORDER BY labour_pct DESC;

Interpretation: a high labour percentage is a starting point for investigation. Check demand, opening hours, management coverage, service and training before recommending fewer hours. NULLIF protects against dividing by zero; an undefined ratio remains NULL.

## Avoid the common join mistake

Joining one store-day sales total directly to ten shifts repeats sales ten times. Group shifts by store_id and date first, then join to the daily table using those two keys. Recheck row count and sales total after the join. Do the same with inventory item and delivery-platform facts.

## 4 Answer operational questions with SQL

03_business_questions.sql contains seven complete queries. Execute one selected query at a time in pgAdmin and explain the result before building a visual.

Weekly trading: v_store_week includes days_loaded. Compare only complete seven-day weeks with the immediately preceding week; a missing week must not become the baseline.

Labour: rank comparable stores by ratio-of-sums labour cost and productivity. Keep team and management definitions separate.

Stock: opening + receipts + transfer-in - transfer-out - closing = actual usage. Actual usage - theoretical usage - waste = unexplained usage. Positive unexplained usage is an investigation signal, not proof of theft.

Purchasing: aggregate receipts by order/line before joining to purchase_orders. Outstanding cases = ordered - received. A short receipt must not be replaced by the ordered quantity.

Delivery: handoff time and adverse issue rate each have their own denominator. Report coverage explicitly; do not relabel the proxy issue rate as the official accuracy metric.

## Worked stock example

Opening 100 kg + received 50 + inbound 5 - outbound 3 - closing 72 = 80 kg actual usage. If theoretical usage is 75 kg and recorded waste is 3 kg, unexplained usage is 2 kg. At £4/kg, total usage cost is £320, including £12 of waste. Deduct £320 once from revenue, not £332.

## Proposed daily analyst workflow

First check whether all expected stores and dates arrived. Reconcile sales to source control totals and paid hours to timekeeping. Review failed checks, then refresh the report. Send an exception list to the agreed operational owner only after definitions are confirmed. Record the loaded-through date and any excluded stores. Reconcile late adjustments in the next controlled run.

This is a proposed batch workflow. The current web dashboard is a historical snapshot; it does not pull live restaurant data. Real refresh timing depends on source access, operational cutoffs and a tested refresh process.

## 5 Build the Power BI model manually

Power BI Desktop runs on Windows, not natively on macOS. Use an available Windows PC or a supported Windows 365/Azure Virtual Desktop environment. The web portfolio can be viewed on the Mac, but it is not a substitute for building and validating a PBIX.

In Power BI Desktop choose Get data > PostgreSQL database. Enter the server and qsr_portfolio database, select Import, authenticate, then choose stores, dim_date, store_daily and any separate detailed facts you need.

If PostgreSQL and Power BI run on the same Windows machine, localhost is suitable. If PostgreSQL runs on your Mac and Power BI runs elsewhere, localhost points to the Windows machine. Use an approved reachable database host/secure connection, or start with CSVs copied to Windows. Do not open the database publicly just for the exercise.

In Power Query set date columns to Date, IDs to Text, hours/costs to Decimal Number and order counts to Whole Number. Check the preview, then Close & Apply.

In Model view create stores[store_id] 1-to-many store_daily[store_id], and dim_date[date] 1-to-many store_daily[date]. Use single-direction filtering from dimensions to facts. Mark dim_date as the date table.

Add each measure from powerbi/measures.dax individually using New measure. Do not paste the entire multi-measure file into a single formula bar. Use the table name store_daily, or update measure references consistently.

## First three measures

Net Sales GBP = SUM(store_daily[net_sales_gbp])

Transactions = SUM(store_daily[transactions])

Average Transaction Value GBP =

 DIVIDE([Net Sales GBP], [Transactions])

Format money as GBP, counts as whole numbers and rates as percentages. DAX rates use 0 to 1; the SQL view labour_cost_pct uses 0 to 100. Do not apply percentage formatting to SQL values such as 20, or the visual will display 2,000%. Prefer DAX measures over averaging stored daily percentages.

## 6 Create five report pages and verify them

## Sales

Cards: net sales, transactions, average ticket, delivery sales share. Line: dim_date[date] and Net Sales GBP. Bar: stores[store_id] and Net Sales GBP. Add store/date slicers. For channels use a separate sales fact filtered by the same dimensions; do not join it directly to store_daily.

## Labour

Cards: paid hours, total labour %, team labour % and transactions per paid hour. Bar: store and productivity. Line: date and labour %. Add scheduled-versus-paid hours and management hours for interpretation.

## Inventory and service

Show food usage, recorded food waste, packaging and handoff. Plot waste as % of net sales by store. Do not sum stock snapshots across dates: ending stock means the closing balance at the selected final count boundary.

## Forecasts

Use forecasts with one model, metric and horizon selected. Show WAPE, bias and MAE. Do not combine sales and transaction error units. origin_date and target_date are distinct date roles; start with target-date filtering.

## Intervention

Use the validated Python result as a fixed analysis table, with outcome, launch date, treatment/control counts, pre/post means, estimate and interval. Show pretrend/placebo caveats. Ordinary store/date slicers must not imply the fixed model has been re-estimated.

## Acceptance checks before publishing

Compare the unfiltered sales/transactions totals to SQL. Filter one store and compare again. Check labour % recalculates from totals. Test a zero denominator and a date with no forecast. Check that a filter affects only the intended facts. Confirm the intervention page remains labelled as a fixed full-panel estimate.

Save QSR_Portfolio.pbix only after these checks. Until you complete this exercise, your CV should say “prepared Power BI measures and model specification”, not “deployed Power BI dashboards”.

## 7 Explain forecasting DID and business value

The forecast origin is the date the prediction was issued. The target is seven days later. Seasonal naive uses the last matching weekday known at origin; the challenger averages four matching weekdays. WAPE = sum absolute errors / sum actuals. Two £100 actuals forecast at £80 and £120 give 20% WAPE, although signed bias is zero.

## Exact simulated intervention design

Operational change: fictional labour planning that raises the generator’s team productivity parameter by 0.3 transactions/hour. Launch: 2 March 2026. Treated stores: F002, F004, F006, F008, F010 and F012. Comparisons: F001, F003, F005, F007, F009 and F011. Before: 5 January–1 March. After: 2 March–26 April. Both periods contain 56 days. Outcome: completed transactions / all paid hours.

Treated means: 6.836 before and 7.029 after, change +0.193. Comparison means: 6.880 and 6.855, change -0.025. DID = +0.193 - (-0.025) = approximately +0.218 orders per paid hour. Store/date fixed effects give the same estimate in this balanced panel; the store-clustered t interval is +0.142 to +0.293.

The pre-period placebo is +0.094 and an early pre-event difference remains. Discuss these limitations openly. There are only 12 clusters. Synthetic assignment and injected changes demonstrate the calculation; they do not verify real operational impact.

## Translate to value carefully

For fixed transactions T, hypothetical hours saved = T × (1/q_before - 1/q_after). Cash benefit requires hours actually removed from cost or redeployed productively, an avoidable wage rate and acceptable service/quality. Do not convert the synthetic DID automatically into annual savings.

Relative change = (new-old)/old. Labour cost from 24% to 22% is a reduction of 2 percentage points, or 8.33% relative. ROI = (incremental cash benefit - programme cost)/programme cost. A cost of zero makes ROI undefined.

## 8 Publish responsibly and prepare for interviews

The portfolio web dashboard is independently published using fictional historical rows. Power BI Service publication is a separate task after the PBIX is built. Import data is a snapshot and needs refresh. A local PostgreSQL server normally needs a reachable gateway for Power BI Service refresh. “Publish to web” exposes the report publicly and requires the relevant tenant/licence settings; use only the fictional dataset.

## A realistic demonstration plan

Explain the business question and the grain of each table in one minute.

Run the SQL for one store, then reproduce the same total in the dashboard.

Show why team labour and total labour percentages differ.

Trace a short receipt through stock usage and explain why waste is counted once.

Walk through the four DID means and point out the placebo limitation.

State clearly what was built, what is proposed, and what needs real source validation.

## CV evidence you still need

Confirm your actual role/title/dates, personal contribution, real store coverage, dashboard users and reporting frequency. Add time saved only when measured. Add workplace intervention outcomes only with real launch/comparison evidence. Keep the synthetic portfolio under Projects if these facts are unavailable.

## Primary references

PostgreSQL macOS — https://www.postgresql.org/download/macosx/

pgAdmin import — https://www.pgadmin.org/docs/pgadmin4/latest/import_export_data.html

psql client commands — https://www.postgresql.org/docs/current/app-psql.html

Power BI Desktop — https://learn.microsoft.com/en-us/power-bi/fundamentals/desktop-get-the-desktop

PostgreSQL connector — https://learn.microsoft.com/en-us/power-query/connectors/postgresql

Power BI refresh — https://learn.microsoft.com/en-us/power-bi/connect-data/refresh-data

Public Power BI embedding — https://learn.microsoft.com/en-us/power-bi/collaborate-share/service-publish-to-web

Fourth scheduling — https://uk.fourth.com/solution/workforce-management/scheduling

Fourth purchasing and receiving — https://uk.fourth.com/solution/inventory-management/purchasing-receiving-invoicing
