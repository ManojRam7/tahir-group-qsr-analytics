# Validation record

Validated locally with Python 3.12 against seed 42. Reproduce with the README commands.

- 23 tests pass: formula boundary cases, deterministic generation, ratio-of-sums, no repeated
  VAT removal or waste double counting, negative mutation tests for receipts/wages/stock/
  waste/counts/transfers, key/orphan/coverage failures, future-actual perturbation, forecast
  error cancellation, SQL/Python parity, staffing scenario leakage and controlled DID recovery.
- Full generator and analysis runner complete: 16 tables, 12 fictional restaurants, 112 dates,
  1,344 store-days, 26,880 channel/daypart sales rows and 14,976 dated forecast evaluations.
- Notebook executes top-to-bottom; all four saved chart outputs were visually inspected for
  labels, units, populations, interval interpretation and clipping. HTML export succeeds.
  Full browser presentation inspection was unavailable because local-file navigation was blocked.
- Lint, formatting, publication guard and diff whitespace checks pass. No private source images,
  PDF, emails or internal figures were staged. The old example CSV was regenerated with generic
  fictional restaurant labels and corrected ex-tax semantics.
- CI executes generation, tests, analysis and notebook on Python 3.11/3.12. See the pull request's
  checks for the actual hosted run status; local execution alone does not certify hosted CI.

## Interpretation limits

The DID scenario returns a positive productivity difference, but also a nonzero pre-period
placebo and an early pre-event gap. The notebook shows these diagnostics. Twelve store clusters,
synthetic treatment assignment and injected effects do not support real causal conclusions.
Forecast benchmarks are evaluated on shared rolling origins, not a held-out production trial.
Labour output is a whole-day staffing scenario, not a deployable station schedule.

SQL also passed PostgreSQL 18.6 validation in an isolated temporary local cluster: all 16 imports,
five views and seven business queries executed successfully. All row counts, daily KPI ratios,
stock balances, forecast error metrics and the manual DID matched Python. The CI PostgreSQL job
repeats these checks. Power BI/DAX relationships, filter behaviour and a `.pbix` report still
require validation on Windows. No live source-system adapters or official
scorecard calculation are claimed. Gaps and production inputs are listed in `source_evidence.md`.

## Portfolio delivery

All five dashboard pages rendered and the store filter was checked against source totals.
Publication uploaded and read back the full HTML and 1,604 reviewed rows with matching SHA-256 hashes.
Public access was confirmed. The source data is a historical synthetic snapshot, not a live feed.
The interview brief renders to one page and the manual guide to nine pages.
