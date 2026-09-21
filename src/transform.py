from __future__ import annotations

import pandas as pd

from .config import SELECTED_COLUMNS


def prepare_curated_dataset(df: pd.DataFrame) -> pd.DataFrame:
    missing = [c for c in SELECTED_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(f"Required source columns are missing: {missing}")

    out = df[SELECTED_COLUMNS].copy()

    out["year"] = pd.to_numeric(out["year"], errors="coerce").astype("Int64")
    out = out.dropna(subset=["country", "year"])
    out["year"] = out["year"].astype(int)

    for col in SELECTED_COLUMNS:
        if col not in {"country", "iso_code", "year"}:
            out[col] = pd.to_numeric(out[col], errors="coerce")

    out = out.drop_duplicates(subset=["country", "year"], keep="last")
    out = out.sort_values(["country", "year"]).reset_index(drop=True)

    return out


def add_derived_indicators(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    grouped = out.groupby("country", group_keys=False)

    if "electricity_demand" in out:
        out["electricity_demand_yoy_pct"] = grouped["electricity_demand"].pct_change() * 100

    if "primary_energy_consumption" in out:
        out["primary_energy_yoy_pct"] = grouped["primary_energy_consumption"].pct_change() * 100

    if "renewables_share_elec" in out:
        out["renewables_share_elec_change_pp"] = grouped["renewables_share_elec"].diff()

    if "fossil_share_elec" in out:
        out["fossil_share_elec_change_pp"] = grouped["fossil_share_elec"].diff()

    if "electricity_demand" in out:
        out["electricity_demand_3y_ma"] = (
            grouped["electricity_demand"]
            .rolling(3, min_periods=3)
            .mean()
            .reset_index(level=0, drop=True)
        )

    return out
