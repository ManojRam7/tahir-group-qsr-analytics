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

SQL is executed through DuckDB for compatible query/parity checks. A live PostgreSQL server and
Power BI/DAX engine were not available; PostgreSQL deployment, DAX relationships/filter behaviour
and a `.pbix` report still require platform validation. No live source-system adapters or official
scorecard calculation are claimed. Gaps and production inputs are listed in `source_evidence.md`.
