from __future__ import annotations

import json
import os
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")

host = os.environ["POSTGRES_HOST"]
port = os.environ.get("POSTGRES_PORT", "5432")
db = os.environ["POSTGRES_DB"]
user = os.environ["POSTGRES_USER"]
password = os.environ["POSTGRES_PASSWORD"]

engine = create_engine(
    f"postgresql+psycopg://{user}:{password}@{host}:{port}/{db}",
    pool_pre_ping=True,
)

schema = (ROOT / "sql" / "schema.sql").read_text(encoding="utf-8")

with engine.begin() as conn:
    for statement in [s.strip() for s in schema.split(";") if s.strip()]:
        conn.execute(text(statement))

energy = pd.read_csv(ROOT / "data" / "processed" / "curated_energy.csv")
metrics = pd.read_csv(ROOT / "data" / "processed" / "market_metrics.csv")

geography = energy[["country", "iso_code"]].drop_duplicates()
geography.to_sql("dim_geography", engine, if_exists="append", index=False, method="multi")

# Avoid duplicate insertion on reruns by using temporary staging tables.
with engine.begin() as conn:
    conn.execute(text("TRUNCATE TABLE fact_energy_annual, fact_market_metrics, fact_forecast, fact_data_quality"))

energy.to_sql("fact_energy_annual", engine, if_exists="append", index=False, method="multi")
metrics.to_sql("fact_market_metrics", engine, if_exists="append", index=False, method="multi")

forecast_path = ROOT / "data" / "processed" / "forecast.csv"
if forecast_path.exists():
    forecast = pd.read_csv(forecast_path)
    forecast.to_sql("fact_forecast", engine, if_exists="append", index=False, method="multi")

quality_path = ROOT / "data" / "quality" / "quality_report.json"
if quality_path.exists():
    quality = json.loads(quality_path.read_text(encoding="utf-8"))
    quality_rows = pd.DataFrame(
        [{"check_name": k, "check_value": json.dumps(v)} for k, v in quality.items()]
    )
    quality_rows.to_sql("fact_data_quality", engine, if_exists="append", index=False, method="multi")

print("PostgreSQL load completed.")
