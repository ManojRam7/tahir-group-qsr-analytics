# Tahir Group QSR Analytics

End-to-end portfolio project for **restaurant sales, labour, waste, service, forecasting and causal impact analysis** using **synthetic data only**.

> **Important:** this repository is an educational/portfolio reconstruction. It does not contain or claim to reproduce confidential Tahir Group or KFC operational data, and all stores, employees, values and intervention results are synthetic.

## Why this project exists

A restaurant data analyst typically works across POS sales, labour scheduling/timekeeping, inventory/waste, service-performance and customer-feedback data. The challenge is not just building charts: it is defining the right grain, reconciling source systems, engineering decision-ready KPIs and proving whether an apparent improvement is actually incremental.

This project demonstrates that complete workflow.

## Business questions

- How are sales, transactions and average transaction value changing by store and period?
- Is labour aligned with demand?
- Which stores have high labour cost despite normal sales?
- Are food cost and waste controlled?
- Does slower service correlate with complaints or lost throughput?
- How accurate are store sales forecasts?
- Did a labour-planning intervention improve productivity beyond the change seen in untreated stores?
- What is the financial impact and ROI of an improvement programme?

## Repository structure

```text
.
├── data/
│   └── sample_store_daily.csv
├── docs/
│   ├── data_dictionary.md
│   └── methodology.md
├── notebooks/
│   └── 01_end_to_end_qsr_analytics.ipynb
├── powerbi/
│   └── measures.dax
├── scripts/
│   ├── generate_synthetic_data.py
│   └── run_analysis.py
├── sql/
│   └── operational_kpis.sql
├── src/qsr_analytics/
│   ├── __init__.py
│   ├── did.py
│   └── metrics.py
├── tests/
│   └── test_metrics.py
├── .github/workflows/ci.yml
├── requirements.txt
└── README.md
```

## Data model

### `store_daily`

Grain: **one row per store per trading date**.

Example observed fields:

`date`, `store_id`, `store_name`, `region`, `transactions`, `net_sales_gbp`, `forecast_sales_gbp`, `paid_hours`, `wage_cost_gbp`, `food_cost_gbp`, `waste_cost_gbp`, `avg_service_seconds`, `complaints`, `promo_flag`, `delivery_mix_pct`, `weather_index`, `local_event_flag`, `treated_store`, `post_period`.

### `employee_shifts`

Grain: **one row per employee shift**.

Fields include `shift_id`, `date`, `store_id`, `employee_id`, `role`, `scheduled_hours`, `paid_hours`, `absence_flag`, `overtime_hours`.

**Critical modelling rule:** aggregate shift data to store/day before joining it to store/day sales. A direct join multiplies sales by the number of shift rows and produces incorrect dashboards.

See [`docs/data_dictionary.md`](docs/data_dictionary.md) for the full dictionary.

## KPI mathematics

Assume sales include 20% VAT in this synthetic example.

| KPI | Formula |
|---|---|
| Revenue ex VAT | `Net Sales / 1.20` |
| Average Transaction Value | `Net Sales / Transactions` |
| Transactions per Paid Hour | `Transactions / Paid Hours` |
| Sales per Paid Hour | `Net Sales / Paid Hours` |
| Labour Cost % | `Wage Cost / Revenue ex VAT × 100` |
| Food Cost % | `Food Cost / Revenue ex VAT × 100` |
| Waste % Sales | `Waste Cost / Revenue ex VAT × 100` |
| Complaints / 1,000 Orders | `Complaints / Transactions × 1000` |
| APE | `ABS(Actual Sales - Forecast Sales) / Actual Sales × 100` |
| Contribution Profit | `Revenue ex VAT - Food Cost - Wage Cost - Waste Cost` |

The Python implementation is in [`src/qsr_analytics/metrics.py`](src/qsr_analytics/metrics.py). Equivalent PostgreSQL and DAX definitions are included in `sql/` and `powerbi/`.

## Measuring improvement correctly

### 1. Simple before/after

For an outcome `Y`:

```text
BeforeAfter = Mean(Y after) - Mean(Y before)
```

Useful descriptively, but not enough for causal attribution because seasonality, weather, promotions or economy-wide changes may occur at the same time.

### 2. Difference-in-differences

Compare treated stores with a control group over the same dates:

```text
DID = (Treated Post - Treated Pre)
    - (Control Post - Control Pre)
```

Example:

```text
Treated productivity:  7.0 -> 7.5 = +0.5
Control productivity:  7.1 -> 7.3 = +0.2
DID effect:                     +0.3 transactions/paid hour
```

The incremental estimate is **+0.3**, not the raw +0.5 treated-store improvement.

### 3. Regression DID

The project estimates:

```text
Y_it = StoreFE_i + DateFE_t + beta(Treated_i × Post_t) + error_it
```

`beta` is the DID effect. Store fixed effects absorb stable store differences; date fixed effects absorb common daily shocks. Standard errors are clustered at store level.

See [`docs/methodology.md`](docs/methodology.md) for assumptions, interpretation, improvement formulas and ROI mathematics.

## Difference-in-differences assumptions

Before interpreting a DID coefficient causally, investigate:

- parallel pre-treatment trends;
- no anticipatory behaviour before launch;
- no treatment spillover to control stores;
- stable store composition;
- no other treated-only policy change starting simultaneously.

A production-grade extension should add event-study coefficients and pre-trend tests.

## ROI

If annual incremental benefit is `B` and programme cost is `K`:

```text
Net Benefit = B - K
ROI = (B - K) / K
Benefit-Cost Multiple = B / K
```

Example: benefit = £65,000 and cost = £25,000.

- Net benefit = £40,000
- Net ROI = 160%
- Benefit-cost multiple = 2.6x

These are different metrics and should be labelled separately.

## Running the project

```bash
python -m venv .venv
source .venv/bin/activate        # macOS/Linux
# .venv\Scripts\activate         # Windows
pip install -r requirements.txt
python scripts/generate_synthetic_data.py
python scripts/run_analysis.py
pytest -q
```

The generator creates deterministic synthetic store-day and employee-shift files under `data/generated/`.

Open the notebook after data generation:

```bash
jupyter notebook notebooks/01_end_to_end_qsr_analytics.ipynb
```

## Power BI dashboard design

A practical report can be organised into four pages:

1. **Executive Performance** — Sales, transactions, ATV, contribution profit, labour %, food %, waste % and forecast accuracy.
2. **Sales & Demand** — Store/date trends, promotion effect, delivery mix, weekday/daypart and actual vs forecast.
3. **Labour & Operations** — Paid hours, wage cost, transactions/hour, sales/hour, overtime, absence, service time and complaints.
4. **Intervention & ROI** — Treated/control pre-post trends, DID effect, confidence interval, operational benefit and ROI.

Reusable DAX measures are provided in [`powerbi/measures.dax`](powerbi/measures.dax).

## What an analyst should learn from this project

- how to identify fact-table grain;
- why cross-grain joins can silently corrupt totals;
- how restaurant sales and labour KPIs are calculated;
- how to reconcile operational and financial measures;
- how to analyse stores using Python, SQL and Power BI;
- the difference between absolute change, relative change and percentage-point change;
- why before/after analysis does not prove causality;
- how DID removes a common counterfactual trend;
- how fixed effects and clustered standard errors improve the evaluation;
- how operational effects translate into financial benefit and ROI.

## Validation

The repository contains unit tests for KPI formulas and DID arithmetic and a GitHub Actions workflow that:

1. installs dependencies;
2. runs tests;
3. generates the synthetic data;
4. runs the analysis pipeline.

## Next extensions

The natural next build stages are:

- product/SKU-level menu-mix analysis;
- hourly/daypart demand modelling;
- labour requirement forecasting;
- actual vs theoretical food cost;
- inventory variance and stock-loss analytics;
- employee attendance/retention analysis;
- event-study DID and placebo tests;
- Power BI `.pbix` implementation using the supplied model and DAX.
