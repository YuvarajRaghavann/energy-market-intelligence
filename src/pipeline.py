from __future__ import annotations

import argparse
import json

from .analytics import build_market_metrics
from .config import PROCESSED_DIR, QUALITY_DIR, RAW_DIR
from .forecast import forecast_indicator
from .ingest import download_energy_data, load_raw_data
from .quality import run_quality_checks
from .transform import add_derived_indicators, prepare_curated_dataset


def run(country: str, indicator: str, horizon: int) -> None:
    raw_path = RAW_DIR / "owid-energy-data.csv"

    if not raw_path.exists():
        print("Downloading latest OWID energy dataset...")
        download_energy_data(raw_path)

    raw = load_raw_data(raw_path)
    quality = run_quality_checks(raw)

    curated = prepare_curated_dataset(raw)
    curated = add_derived_indicators(curated)

    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    QUALITY_DIR.mkdir(parents=True, exist_ok=True)

    curated.to_csv(PROCESSED_DIR / "curated_energy.csv", index=False)

    metrics = build_market_metrics(curated)
    metrics.to_csv(PROCESSED_DIR / "market_metrics.csv", index=False)

    with open(QUALITY_DIR / "quality_report.json", "w", encoding="utf-8") as f:
        json.dump(quality, f, indent=2)

    result = forecast_indicator(
        curated,
        country=country,
        indicator=indicator,
        horizon=horizon,
    )
    result.forecast.to_csv(PROCESSED_DIR / "forecast.csv", index=False)
    result.metrics.to_csv(PROCESSED_DIR / "forecast_model_metrics.csv", index=False)

    print("Pipeline complete.")
    print(f"Curated rows: {len(curated):,}")
    print(f"Forecast country: {country}")
    print(f"Forecast indicator: {indicator}")
    print(f"Best model by mean CV MAE: {result.metrics.iloc[0]['model']}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--country", default="India")
    parser.add_argument("--indicator", default="electricity_demand")
    parser.add_argument("--horizon", type=int, default=3)
    args = parser.parse_args()
    run(args.country, args.indicator, args.horizon)
