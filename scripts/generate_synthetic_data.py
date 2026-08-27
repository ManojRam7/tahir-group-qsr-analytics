from pathlib import Path

import numpy as np
import pandas as pd


SEED = 42
VAT_RATE = 0.20
INTERVENTION_DATE = pd.Timestamp("2026-04-01")


def generate_store_daily(seed: int = SEED) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    dates = pd.date_range("2026-01-01", "2026-06-30", freq="D")
    stores = pd.DataFrame(
        [
            ("S001", "Birmingham Central", "West Midlands", 1, 1.12),
            ("S002", "Birmingham South", "West Midlands", 1, 0.96),
            ("S003", "Coventry", "West Midlands", 1, 1.02),
            ("S004", "Wolverhampton", "West Midlands", 1, 0.93),
            ("S005", "Leicester", "East Midlands", 0, 1.05),
            ("S006", "Derby", "East Midlands", 0, 0.97),
            ("S007", "Nottingham", "East Midlands", 0, 1.08),
            ("S008", "Stoke", "West Midlands", 0, 0.91),
        ],
        columns=["store_id", "store_name", "region", "treated_store", "store_factor"],
    )
    rows = []
    for _, store in stores.iterrows():
        for date in dates:
            dow = date.dayofweek
            weekend = dow >= 4
            season = 1 + 0.05 * np.sin(2 * np.pi * date.dayofyear / 365)
            demand = 390 * store.store_factor * season * (1.18 if weekend else 1.0)
            transactions = max(80, int(rng.normal(demand, 25)))
            post = int(date >= INTERVENTION_DATE)
            did = int(store.treated_store * post)

            atv = rng.normal(11.1, 0.45) * (1 + 0.006 * post)
            net_sales = transactions * atv

            base_tph = rng.normal(7.1, 0.28)
            productivity_effect = 0.30 * did
            tph = max(4.0, base_tph + productivity_effect)
            paid_hours = transactions / tph
            hourly_wage = rng.normal(12.8, 0.35)
            wage_cost = paid_hours * hourly_wage

            revenue_ex_vat = net_sales / (1 + VAT_RATE)
            food_cost = revenue_ex_vat * rng.normal(0.305, 0.012)
            waste_rate = max(0.006, rng.normal(0.020 - 0.0025 * did, 0.003))
            waste_cost = revenue_ex_vat * waste_rate
            service_seconds = max(70, rng.normal(182 - 15 * did, 12))
            complaints = rng.poisson(transactions * max(0.0005, 0.0032 - 0.0005 * did))
            forecast_sales = net_sales * (1 + rng.normal(0, 0.055 - 0.008 * did))

            rows.append(
                {
                    "date": date.date().isoformat(),
                    "store_id": store.store_id,
                    "store_name": store.store_name,
                    "region": store.region,
                    "treated_store": int(store.treated_store),
                    "post_period": post,
                    "transactions": transactions,
                    "net_sales_gbp": round(net_sales, 2),
                    "forecast_sales_gbp": round(forecast_sales, 2),
                    "paid_hours": round(paid_hours, 2),
                    "wage_cost_gbp": round(wage_cost, 2),
                    "food_cost_gbp": round(food_cost, 2),
                    "waste_cost_gbp": round(waste_cost, 2),
                    "avg_service_seconds": round(service_seconds, 1),
                    "complaints": int(complaints),
                    "promo_flag": int(rng.random() < 0.14),
                    "delivery_mix_pct": round(float(np.clip(rng.normal(0.24, 0.035), 0.10, 0.40)) * 100, 2),
                    "weather_index": round(float(rng.normal(0, 1)), 3),
                    "local_event_flag": int(rng.random() < 0.04),
                }
            )
    return pd.DataFrame(rows)


def generate_employee_shifts(store_daily: pd.DataFrame, seed: int = SEED + 1) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    rows = []
    shift_id = 1
    for row in store_daily.itertuples(index=False):
        n_staff = max(5, int(round(row.paid_hours / 7.0)))
        allocated = rng.dirichlet(np.ones(n_staff)) * row.paid_hours
        for i, hours in enumerate(allocated, start=1):
            scheduled = max(hours, hours + rng.normal(0.15, 0.25))
            rows.append(
                {
                    "shift_id": f"SH{shift_id:07d}",
                    "date": row.date,
                    "store_id": row.store_id,
                    "employee_id": f"{row.store_id}-E{i:03d}",
                    "role": rng.choice(["Team Member", "Cook", "Shift Manager"], p=[0.60, 0.25, 0.15]),
                    "scheduled_hours": round(float(scheduled), 2),
                    "paid_hours": round(float(hours), 2),
                    "absence_flag": int(rng.random() < 0.025),
                    "overtime_hours": round(float(max(0, hours - 8)), 2),
                }
            )
            shift_id += 1
    return pd.DataFrame(rows)


def main():
    output = Path("data/generated")
    output.mkdir(parents=True, exist_ok=True)
    daily = generate_store_daily()
    shifts = generate_employee_shifts(daily)
    daily.to_csv(output / "store_daily.csv", index=False)
    shifts.to_csv(output / "employee_shifts.csv", index=False)
    print(f"Generated {len(daily):,} store-day rows and {len(shifts):,} shift rows")


if __name__ == "__main__":
    main()
