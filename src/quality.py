from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd

from .config import KEY_COLUMNS, NON_NEGATIVE_COLUMNS


def _iqr_outlier_count(series: pd.Series) -> int:
    values = pd.to_numeric(series, errors="coerce").dropna()
    if len(values) < 8:
        return 0
    q1 = values.quantile(0.25)
    q3 = values.quantile(0.75)
    iqr = q3 - q1
    if iqr == 0:
        return 0
    lower = q1 - 1.5 * iqr
    upper = q3 + 1.5 * iqr
    return int(((values < lower) | (values > upper)).sum())


def run_quality_checks(df: pd.DataFrame) -> dict[str, Any]:
    report: dict[str, Any] = {
        "row_count": int(len(df)),
        "column_count": int(len(df.columns)),
        "duplicate_country_year_rows": int(df.duplicated(KEY_COLUMNS).sum()),
        "missingness": {},
        "negative_values": {},
        "annual_gap_checks": {},
        "potential_outliers_iqr": {},
    }

    for col in df.columns:
        missing = int(df[col].isna().sum())
        if missing:
            report["missingness"][col] = {
                "count": missing,
                "rate": round(missing / max(len(df), 1), 6),
            }

    for col in NON_NEGATIVE_COLUMNS:
        if col in df.columns:
            values = pd.to_numeric(df[col], errors="coerce")
            count = int((values < 0).sum())
            report["negative_values"][col] = count

    if "country" in df.columns and "year" in df.columns:
        grouped = df.dropna(subset=["country", "year"]).sort_values(["country", "year"])
        grouped["year_diff"] = grouped.groupby("country")["year"].diff()
        gaps = grouped[grouped["year_diff"] > 1]
        report["annual_gap_checks"] = {
            "rows_with_year_gap": int(len(gaps)),
            "countries_with_year_gaps": int(gaps["country"].nunique()),
        }

    for col in NON_NEGATIVE_COLUMNS:
        if col in df.columns:
            report["potential_outliers_iqr"][col] = _iqr_outlier_count(df[col])

    report["quality_pass"] = bool(
        report["duplicate_country_year_rows"] == 0
        and all(v == 0 for v in report["negative_values"].values())
    )
    return report
