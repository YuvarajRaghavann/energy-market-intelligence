from __future__ import annotations

import numpy as np
import pandas as pd


def cagr(start_value: float, end_value: float, years: int) -> float | None:
    if years <= 0 or start_value <= 0 or end_value < 0:
        return None
    return (end_value / start_value) ** (1 / years) - 1


def build_market_metrics(df: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict] = []

    for country, g in df.groupby("country"):
        g = g.sort_values("year")
        if g.empty:
            continue

        latest = g.iloc[-1]
        current_year = int(latest["year"])
        row = {
            "country": country,
            "latest_year": current_year,
            "latest_electricity_demand_twh": latest.get("electricity_demand"),
            "latest_primary_energy_twh": latest.get("primary_energy_consumption"),
            "latest_renewables_share_elec_pct": latest.get("renewables_share_elec"),
            "latest_fossil_share_elec_pct": latest.get("fossil_share_elec"),
        }

        for lookback in (3, 5):
            prior = g[g["year"] <= current_year - lookback]
            if not prior.empty and pd.notna(prior.iloc[-1].get("electricity_demand")) and pd.notna(latest.get("electricity_demand")):
                row[f"electricity_demand_{lookback}y_cagr_pct"] = (
                    cagr(float(prior.iloc[-1]["electricity_demand"]), float(latest["electricity_demand"]), lookback) * 100
                )

        rows.append(row)

    return pd.DataFrame(rows)
