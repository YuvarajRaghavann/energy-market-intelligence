# Energy Market Intelligence & Forecasting Platform

A portfolio-grade energy-data analytics project designed around the workflow of a data/research analyst:

**collect → clean → validate → model → analyze → forecast → communicate**

The project uses the public **Our World in Data Energy** dataset as its primary demonstration source. The dataset is updated regularly and combines energy indicators sourced from organizations including the Energy Institute, U.S. EIA and Ember. The project does **not** use Rystad proprietary data.

## Why this project exists

This project is intentionally aligned to the skills demonstrated in the Rystad Energy Analyst (Data & Research) job description:

- Python and SQL
- data collection, cleaning and validation
- structured database design
- Python automation
- statistical analysis and quantitative methods
- machine learning and forecasting
- AI-enabled research workflows
- analytical outputs and dashboards
- methodology, assumptions and limitations

It is a portfolio project, not a claim of professional energy-market research experience.

## Architecture

```text
Public energy dataset
        │
        ▼
src/ingest.py
        │
        ▼
Raw CSV
        │
        ▼
src/quality.py ─────► quality_report.json
        │
        ▼
src/transform.py
        │
        ├──────────────► curated_energy.csv
        │
        ▼
src/analytics.py
        │
        ├──────────────► market_metrics.csv
        │
        ▼
src/forecast.py
        │
        ├──────────────► forecast.csv
        │
        ▼
Streamlit dashboard / Power BI
```

## Data source

Primary source:

- Our World in Data, Energy dataset: https://owid-public.owid.io/data/energy/owid-energy-data.csv
- OWID repository and codebook: https://github.com/owid/energy-data

The OWID dataset is one row per location and year and includes metrics for energy consumption, electricity, energy mix and related indicators. OWID documents the underlying sources and processing methodology in its repository and codebook.

Additional source for methodology/background:

- IEA World Energy Statistics: https://www.iea.org/data-and-statistics/data-product/world-energy-statistics

Use source pages as the authoritative reference for definitions, units and licensing before publishing derived work.

## Research questions

The dashboard and analysis are designed to answer questions such as:

1. How has electricity demand changed over time by country?
2. How have oil, gas, coal and renewable energy indicators changed?
3. How does the electricity mix differ across regions?
4. What are the recent growth rates and trend changes?
5. Can a simple time-series ML model provide a transparent short-horizon forecast?
6. Where does the input data require quality review before interpretation?

## Features

### 1. Data ingestion
Downloads the latest OWID energy CSV at runtime and stores a reproducible local raw copy.

### 2. Data-quality checks
Checks:
- duplicate country-year keys
- missingness
- negative values in non-negative energy indicators
- suspicious gaps in annual observations
- potential statistical outliers using IQR
- schema/column presence

Potential outliers are **flagged, not silently deleted**.

### 3. Data transformation
Creates a focused analytical dataset with:
- geography
- population and GDP
- primary energy consumption
- electricity demand/generation
- fossil and renewable shares
- oil/gas/coal production and consumption
- selected low-carbon generation indicators

### 4. Market analytics
Calculates:
- year-over-year growth
- rolling 3-year averages
- 5-year CAGR when enough history exists
- fossil vs renewable electricity share comparison
- production/consumption indicators

### 5. Forecasting
For a selected country and indicator:
- Naive last-value baseline
- linear trend baseline
- Random Forest regression using lagged values and rolling features
- time-series cross-validation
- MAE and RMSE comparison
- recursive short-horizon forecast

The project prioritizes transparency over pretending that a small annual dataset can produce a production-grade market forecast.

### 6. Dashboard
The Streamlit app provides:
- country selection
- indicator selection
- historical trend charts
- growth metrics
- electricity mix view
- forecast view
- data-quality summary

### 7. SQL layer
Includes PostgreSQL DDL for:
- `dim_geography`
- `fact_energy_annual`
- `fact_market_metrics`
- `fact_forecast`
- `fact_data_quality`

## Quick start

### 1. Create environment

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate
```

### 2. Install

```bash
pip install -r requirements.txt
```

### 3. Run the pipeline

```bash
python -m src.pipeline --country "India" --indicator electricity_demand --horizon 3
```

This creates:

```text
data/raw/owid-energy-data.csv
data/processed/curated_energy.csv
data/processed/market_metrics.csv
data/processed/forecast.csv
data/quality/quality_report.json
```

### 4. Launch dashboard

```bash
streamlit run app.py
```

### 5. Optional PostgreSQL load

Create a database, set environment variables from `.env.example`, then:

```bash
python scripts/load_postgres.py
```

The SQL schema is in `sql/schema.sql`.

## Reproducibility

The raw dataset is intentionally not committed to this repository. Running the ingestion step downloads the current public source. This avoids shipping a large third-party dataset and makes the data refresh explicit.

For an interview, be ready to explain:
- the exact source URL
- retrieval date
- selected fields and units
- validation checks
- why potential outliers were flagged instead of removed
- why time-series validation was used
- why the model should be treated as a research prototype rather than a market prediction engine

## Power BI

A Power BI handoff guide is included in `powerbi/README.md`.

The project exports flat analytical CSV files so they can be loaded into Power BI without changing the core Python pipeline.

## Resume usage

Do not list this project on a resume as completed until you have actually:
1. run the pipeline,
2. inspected the data,
3. built the dashboard,
4. validated the forecasts,
5. pushed the code to GitHub, and
6. can explain the implementation.

See `docs/resume_bullets.md` for resume wording that becomes valid after those steps are completed.

## Project limitations

- Public data sources do not reproduce Rystad's proprietary commercial datasets.
- Annual country-level observations are relatively sparse for sophisticated forecasting.
- Forecasts are analytical demonstrations, not investment or commodity price advice.
- Source datasets can change as upstream organizations publish revisions.
- The project does not claim professional energy-market experience.

## License and attribution

The code in this repository can be licensed separately from the data.

OWID states that its visualizations, data and code are open access under CC BY 4.0, while third-party data in its dataset may retain the original providers' license terms. Always review the current source licensing before redistributing data.

See:
https://github.com/owid/energy-data
