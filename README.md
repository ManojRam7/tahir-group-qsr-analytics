# Tahir Group QSR Analytics

An evidence-informed **synthetic portfolio project** for restaurant sales, labour, inventory,
forecasting and operational intervention analysis. It is not an official system, a calibrated
replica or a claim about real restaurant performance. No private screenshots, emails, store
figures, supplier details or proprietary datasets are included.

The v0.2 redesign follows structural evidence from a privately reviewed 15-page screenshot
compilation. [Evidence and unresolved definitions](docs/source_evidence.md) separates visible
screen facts from proposed mappings and missing data. Every dataset and example value is fictional.

## Portfolio and learning materials

[Open the public five-page dashboard](https://qsr-operations-manoj-portfolio.rams-007.chatgpt.site).
It uses fictional historical data only; it is not a live restaurant feed or a Power BI file.

- [Manual PostgreSQL and Power BI guide](docs/practical_learning_guide.md)
- [One-page interview brief: summary, three points and ten Q&A](docs/interview_one_page.md)
- [Team-focused CV recommendations](docs/cv_recommendations.md)
- [Evidence and assumption register](docs/assumptions_and_cv.md)
- [PostgreSQL schema, views and business queries](sql/postgresql/)
- [Dashboard content and reproducible snapshot](dashboard/)

The learning documents now use the user-described reporting route: Data Analyst/data team →
Business Analysis team of around 6–8 members → Area Coaches and CEO/CTO briefings. The
first-person scripts teach team responsibilities; numerical examples remain synthetic and
employment claims depend on actual personal delivery. Customer-review analysis is specified
as a future requirement; only complaint counts exist in the current model.

## What works

- Sixteen synthetic tables: separate channel/daypart sales; team/manager shifts; delivery,
  service, upgrades and availability; item master, PO lines, short receipts, paired transfers,
  waste, stock counts and inventory balances; dated forecasts and an aggregated store-day mart.
- Deterministic generation for 12 fictional stores and 112 dates, with a fictional common
  intervention, explicit tax and reconciled shift wages, stock quantities and receipt values.
- Fail-fast grain, key, population, chronology, balance and source-to-mart checks. Detail facts
  aggregate independently before one-to-one mart joins.
- Ex-tax net sales, ratio-of-sums KPIs, direct vs all-paid productivity, team vs total labour,
  food usage including waste, packaging cost, weighted elapsed service and delivery metrics.
- Honest rolling-origin seven-day forecasts: seasonal naive and four-week weekday mean,
  separate sales/transactions, warm-up nulls, MAE/RMSE/WAPE/bias and leakage tests.
- Before/after arithmetic, validated common-date DID, store/date fixed effects, clustered
  Student-t intervals, pretrend gaps, pre-period placebo and weekly event-study diagnostics.
- Executable teaching notebook, PostgreSQL SQL checked against Python on PostgreSQL 18 and DuckDB,
  DAX measure templates, CI and privacy checks. DAX requires manual Power BI validation.

## Run locally

Python **3.11 or 3.12** is required.

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -e .
python scripts/generate_synthetic_data.py
python scripts/run_analysis.py
pytest -q
ruff check src scripts tests
python scripts/check_publication.py
jupyter nbconvert --execute --to notebook --inplace notebooks/01_end_to_end_qsr_analytics.ipynb
```

Run from repository root. Generated CSVs live in ignored `data/generated/`; analysis outputs in
ignored `reports/generated/`. No private source file is needed to reproduce the demo. CI runs the
same generation, reconciliation, analysis and notebook execution, plus SQL parity and negative tests.

## Definitions that changed

**Breaking correction:** `net_sales_gbp` now means sales **excluding tax**. Older versions used
the label for VAT-inclusive receipts, then divided by 1.2. Regenerate all old outputs. Gross, net
and tax are separate fields. The generator's uniform fictional tax rate is not a real tax policy.

Food usage includes waste. Contribution = net - food usage - packaging usage - wages; waste is
reported separately but not deducted twice. This is a partial contribution, not EBITDA. Forecasts
are calculated from prior history, never from the actual being forecast. DTPLH, official accuracy,
Gold Standard, WACL and scorecard rules remain unconfirmed; proxy metrics use explicit generic names.

## Repository guide

| Path | Purpose |
|---|---|
| [docs/source_evidence.md](docs/source_evidence.md) | Page-by-page structural evidence and remaining data gaps |
| [docs/architecture.md](docs/architecture.md) | Grain boundaries, accounting and production adapter requirements |
| [docs/data_dictionary.md](docs/data_dictionary.md) | Every generated table and field, units and metric definitions |
| [docs/methodology.md](docs/methodology.md) | Worked examples, before/after, DID, forecasting and ROI scenarios |
| `src/qsr_analytics/` | ETL contracts, metrics, forecasting and causal diagnostics |
| `scripts/` | Generator, analysis runner and publication guard |
| `sql/`, `powerbi/` | SQL queries and DAX templates |
| `notebooks/01_end_to_end_qsr_analytics.ipynb` | Reproducible tutorial with synthetic results |
| `tests/`, `.github/workflows/ci.yml` | Mathematical, reconciliation, leakage and pipeline validation |

## Limits and next real-data requirements

This project implements a working synthetic pipeline, not live RMF/Atlas/MacromatiX adapters.
It does not infer the official fiscal calendar, LY comparable dates, scorecard algorithm,
service boundaries, actual recipes/yields or delivery opportunity formula from cropped screens.
Source-reported scorecard and ranking metrics need separate versioned snapshots; no official
score is fabricated. The public web dashboard is deployed; a `.pbix` file has not been built or validated.

Production calibration requires authorized sanitized exports, original headers, signed-off metric
rules, timekeeping and wage inclusions, receipt/stock/waste/recipe records, immutable forecast
vintages, timer populations and credible intervention history. See the evidence register for the
specific gaps. Keep confidential inputs outside this repository; publication needs separate
explicit authorization. The publication guard is a backstop, not a de-identification guarantee.
