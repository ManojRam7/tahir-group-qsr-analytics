"""Fictional operations, generated independently of all private screenshot figures."""

import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from qsr_analytics.etl import build_mart, validate_tables
from qsr_analytics.forecasting import rolling_forecasts

SEED = 42
INTERVENTION_DATE = pd.Timestamp("2026-03-02")
CHANNELS = ["eat_in", "takeout", "drive_thru", "delivery"]
DAYPARTS = ["before_noon", "midday", "afternoon", "evening", "late"]


def generate_tables(seed=SEED, n_stores=12, days=112):
    if n_stores < 2 or n_stores % 2 or days < 35:
        raise ValueError("Use an even store count >= 2 and at least 35 days")
    rng = np.random.default_rng(seed)
    dates = pd.date_range("2026-01-05", periods=days)
    stores = pd.DataFrame(
        [
            dict(
                store_id=f"F{i:03}",
                store_name=f"Fictional Restaurant {i}",
                region=f"Region {i % 3 + 1}",
                has_drive_thru=int(i % 3 == 0),
                treated_store=int(i % 2 == 0),
            )
            for i in range(1, n_stores + 1)
        ]
    )
    items = pd.DataFrame(
        [
            dict(
                item_id="I001",
                description="Ingredient A",
                category="food",
                base_uom="kg",
                units_per_case=8.0,
                unit_cost_gbp=15.0,
                recipe_units_per_transaction=0.12,
            ),
            dict(
                item_id="I002",
                description="Ingredient B",
                category="food",
                base_uom="kg",
                units_per_case=10.0,
                unit_cost_gbp=8.0,
                recipe_units_per_transaction=0.08,
            ),
            dict(
                item_id="I003",
                description="Packaging A",
                category="packaging",
                base_uom="each",
                units_per_case=100.0,
                unit_cost_gbp=0.08,
                recipe_units_per_transaction=1.0,
            ),
        ]
    )
    sales, shifts, service, delivery, availability, upgrades = [], [], [], [], [], []
    for s in stores.itertuples():
        factor = rng.uniform(0.8, 1.2)
        for date in dates:
            ds = date.date().isoformat()
            effect = s.treated_store * int(date >= INTERVENTION_DATE)
            # Demand and common time shocks precede planning intervention.
            n = int(max(80, rng.normal(340 * factor * (1.2 if date.dayofweek >= 4 else 1), 22)))
            weights = np.array([0.18, 0.40, 0.15 * s.has_drive_thru, 0.27])
            channel_counts = rng.multinomial(n, weights / weights.sum())
            for ch, count in zip(CHANNELS, channel_counts):
                for dp, count_dp in zip(
                    DAYPARTS, rng.multinomial(count, [0.07, 0.21, 0.16, 0.30, 0.26])
                ):
                    net = round(count_dp * rng.uniform(7.5, 10.5), 2)
                    tax = round(net * 0.2, 2)  # fictional uniform tax, not a production rule
                    sales.append(
                        dict(
                            store_id=s.store_id,
                            date=ds,
                            channel=ch,
                            daypart=dp,
                            transactions=count_dp,
                            net_sales_gbp=net,
                            tax_gbp=tax,
                            gross_sales_gbp=round(net + tax, 2),
                        )
                    )
            # Fixed role budgets reconcile to the shift detail; no employee names.
            crew_budget = n / (8.2 + 0.3 * effect)
            for role, budget, rate in [("team", crew_budget, 14.2), ("manager", 10.0, 17.8)]:
                staff = int(np.ceil(budget / 7))
                for j in range(staff):
                    scheduled = round(budget / staff, 4)
                    absent = int(rng.random() < 0.02)
                    paid = 0 if absent else round(max(0, scheduled + rng.normal(0, 0.15)), 4)
                    shifts.append(
                        dict(
                            shift_id=f"SHIFT{len(shifts) + 1:08}",
                            store_id=s.store_id,
                            date=ds,
                            employee_id=f"{s.store_id}-{role}-{j}",
                            role=role,
                            scheduled_hours=scheduled,
                            paid_hours=paid,
                            absence_flag=absent,
                            overtime_hours=max(0, paid - 8),
                            hourly_rate_gbp=rate,
                            wage_cost_gbp=round(paid * rate, 2),
                        )
                    )
            for dp in DAYPARTS:
                orders = sum(r["transactions"] for r in sales[-20:] if r["daypart"] == dp)
                service.append(
                    dict(
                        store_id=s.store_id,
                        date=ds,
                        daypart=dp,
                        service_orders=orders,
                        service_total_seconds=round(
                            orders * max(60, rng.normal(190 - 8 * effect, 14)), 2
                        ),
                        complaints=int(rng.poisson(orders * 0.002)),
                    )
                )
                eligible = orders
                upgraded = int(rng.binomial(eligible, 0.16))
                upgrades.append(
                    dict(
                        store_id=s.store_id,
                        date=ds,
                        daypart=dp,
                        upgrade_eligible_transactions=eligible,
                        upgraded_transactions=upgraded,
                        incremental_upgrade_sales_gbp=round(upgraded * 1.1, 2),
                    )
                )
                for item in items.itertuples():
                    minutes = 180
                    availability.append(
                        dict(
                            store_id=s.store_id,
                            date=ds,
                            daypart=dp,
                            item_id=item.item_id,
                            eligible_minutes=minutes,
                            available_minutes=minutes - int(rng.integers(0, 20)),
                            gold_checks=20,
                            gold_passes=int(rng.binomial(20, 0.98)),
                        )
                    )
            for platform, accepted in zip(
                ["platform_a", "platform_b"], rng.multinomial(channel_counts[3], [0.55, 0.45])
            ):
                rejected = int(rng.binomial(accepted, 0.02))
                delivery.append(
                    dict(
                        store_id=s.store_id,
                        date=ds,
                        platform=platform,
                        accepted_orders=accepted,
                        rejected_orders=rejected,
                        offered_orders=accepted + rejected,
                        handoff_orders=accepted,
                        handoff_total_seconds=round(accepted * rng.uniform(160, 300), 2),
                        delivery_accuracy_eligible_orders=accepted,
                        delivery_issue_orders=int(rng.binomial(accepted, 0.035)),
                        scheduled_minutes=840,
                        offline_minutes=int(rng.integers(0, 40)),
                    )
                )
    sales, shifts = pd.DataFrame(sales), pd.DataFrame(shifts)
    # Orders/receipts are distinct: a purchase order is not stock on hand.
    po, receipts, stock, transfers = [], [], [], []
    daily_orders = sales.groupby(["store_id", "date"]).transactions.sum()
    for s in stores.itertuples():
        for item in items.itertuples():
            opening = 600.0 if item.base_uom == "kg" else 5000.0
            pending = {}
            for i, date in enumerate(dates):
                ds = date.date().isoformat()
                if i % 7 == 0 and i + 2 < days:
                    cases = {"I001": 60, "I002": 30, "I003": 40}[item.item_id]
                    order_id = f"PO{len(po) + 1:06}"
                    due = (date + pd.Timedelta(days=2)).date().isoformat()
                    po.append(
                        dict(
                            order_id=order_id,
                            line_id=1,
                            store_id=s.store_id,
                            item_id=item.item_id,
                            supplier_id="SUPPLIER_FICTIONAL",
                            order_date=ds,
                            due_date=due,
                            ordered_cases=cases,
                            case_price_gbp=item.unit_cost_gbp * item.units_per_case,
                        )
                    )
                    pending[i + 2] = (order_id, cases)
                received = 0.0
                if i in pending:
                    order_id, cases = pending[i]
                    # short receipt: ordered quantities never substituted for receipt quantities
                    received_cases = cases - 1
                    received = received_cases * item.units_per_case
                    receipts.append(
                        dict(
                            receipt_id=f"R{len(receipts) + 1:06}",
                            order_id=order_id,
                            line_id=1,
                            store_id=s.store_id,
                            item_id=item.item_id,
                            receipt_date=ds,
                            received_cases=received_cases,
                            units_per_case=item.units_per_case,
                            received_units=received,
                            receipt_value_gbp=round(received * item.unit_cost_gbp, 2),
                        )
                    )
                theoretical = daily_orders.loc[(s.store_id, ds)] * item.recipe_units_per_transaction
                waste = round(theoretical * rng.uniform(0.01, 0.04), 4)
                unexplained = round(theoretical * rng.uniform(0, 0.01), 4)
                amount = (10.0 if item.base_uom == "kg" else 100.0) if i % 14 == 7 else 0.0
                number = int(s.store_id[1:])
                transfer_in = amount if number % 2 == 0 else 0.0
                transfer_out = amount if number % 2 == 1 and number < n_stores else 0.0
                if transfer_out:
                    transfers.append(
                        dict(
                            transfer_id=f"TR{len(transfers) + 1:06}",
                            date=ds,
                            from_store_id=s.store_id,
                            to_store_id=f"F{number + 1:03}",
                            item_id=item.item_id,
                            units=amount,
                        )
                    )
                closing = round(
                    opening
                    + received
                    + transfer_in
                    - transfer_out
                    - theoretical
                    - waste
                    - unexplained,
                    4,
                )
                stock.append(
                    dict(
                        store_id=s.store_id,
                        date=ds,
                        item_id=item.item_id,
                        opening_units=opening,
                        received_units=received,
                        transfer_in_units=transfer_in,
                        transfer_out_units=transfer_out,
                        theoretical_usage_units=theoretical,
                        waste_units=waste,
                        closing_units=closing,
                        unit_cost_gbp=item.unit_cost_gbp,
                    )
                )
                opening = closing
    tables = dict(
        stores=stores,
        items=items,
        sales=sales,
        employee_shifts=shifts,
        service=pd.DataFrame(service),
        delivery=pd.DataFrame(delivery),
        availability=pd.DataFrame(availability),
        upgrades=pd.DataFrame(upgrades),
        purchase_orders=pd.DataFrame(po),
        receipts=pd.DataFrame(receipts),
        stock=pd.DataFrame(stock),
    )
    tables["transfers"] = pd.DataFrame(transfers)
    tables["waste"] = tables["stock"][["store_id", "date", "item_id", "waste_units"]].copy()
    tables["waste"]["waste_id"] = [f"W{i:07}" for i in range(len(stock))]
    tables["waste"]["reason"] = "fictional_spoilage"
    tables["stock_counts"] = tables["stock"][
        ["store_id", "date", "item_id", "closing_units"]
    ].copy()
    tables["stock_counts"]["count_location"] = "all_locations_consolidated"
    tables["forecasts"] = rolling_forecasts(sales)
    tables["store_daily"] = build_mart(tables)
    validate_tables(tables)
    return tables


def generate_store_daily(seed=SEED):
    return generate_tables(seed)["store_daily"]


def main():
    output = Path("data/generated")
    output.mkdir(parents=True, exist_ok=True)
    for name, table in generate_tables().items():
        table.to_csv(output / f"{name}.csv", index=False)
        print(f"{name}: {len(table):,} rows")


if __name__ == "__main__":
    main()
