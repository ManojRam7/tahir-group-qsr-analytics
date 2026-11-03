# Published QSR portfolio dashboard

[Open the public dashboard](https://qsr-operations-manoj-portfolio.rams-007.chatgpt.site).

Five pages cover Sales, Labour, Inventory & service, Forecasts and Intervention.
The 12 stores and every result are fictional. This is a historical snapshot of
5 January–26 April 2026, generated on 2 November 2026, with no live restaurant connection.

`DashboardContent.jsx` and `qsr.css` preserve the authored visual content for review.
They use the Data app component runtime; these two files alone are not a standalone website.
The complete hosted code has a separate Sites source history. Runtime and deployment credentials
are excluded from this public analytics repository.

To reproduce reviewed data, run from the repository root:

```sh
python scripts/generate_synthetic_data.py
python scripts/run_analysis.py
python scripts/export_dashboard_snapshot.py
```

The last command writes `reports/generated/dashboard_snapshot.json` from validated data.
`snapshot_template.json` contains query provenance and the existing logical dashboard identity.
Copy the generated snapshot into `src/data.json` of the existing Data authoring app,
and the two content files into `src/content/dashboard/`. Build with the installed Data app
builder and verify charts and filters before republishing the same Site. A separate new
dashboard needs a new identity. Reproduction of the data and calculations requires only Python;
rebuilding this specific web UI requires the Data app runtime.

Store filtering applies to Sales, Labour and Inventory & service. Forecasts and Intervention
use the explicitly labelled full portfolio. Channel values aggregate the complete date window.
Ratios recompute from their additive numerator and denominator. The DID estimator averages
store-day productivity, so it deliberately differs from portfolio ratio-of-sums productivity.

Validation: all five pages rendered; store F001 changed net sales to £412,722 and transactions
to 45,671; clearing the filter restored £4,549,410 and 505,018. Hosted HTML and the complete
1,604-row reviewed snapshot passed SHA-256 readback verification. Source inspector and card
exports belong to the shared runtime. Hosted owner editing has not been asserted or tested.

The Power BI exercise is documented separately. This web app is not a PBIX file.
