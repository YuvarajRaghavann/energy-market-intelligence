# Power BI handoff

The Python pipeline exports flat CSV files for dashboarding:

- `data/processed/curated_energy.csv`
- `data/processed/market_metrics.csv`
- `data/processed/forecast.csv`

## Suggested model

Use `curated_energy.csv` as the main fact table.

Recommended relationships:

```text
dim_geography[Country] 1 ─── * curated_energy[Country]
```

A separate date table can be created in Power BI from the `year` column.

## Suggested report pages

### Page 1: Market Overview
Cards:
- latest electricity demand
- YoY growth
- primary energy consumption
- renewable electricity share
- fossil electricity share

Visuals:
- demand trend
- renewable vs fossil share trend
- country comparison

### Page 2: Supply / Demand
Visuals:
- oil production
- gas production
- coal production
- corresponding consumption indicators

### Page 3: Forecast
Use `forecast.csv`:
- historical actuals
- forecast
- selected model
- cross-validation MAE / RMSE from `forecast_model_metrics.csv`

## Example DAX

```DAX
Electricity Demand TWh =
SUM(curated_energy[electricity_demand])

Renewables Share % =
AVERAGE(curated_energy[renewables_share_elec])

Fossil Share % =
AVERAGE(curated_energy[fossil_share_elec])

YoY Electricity Demand % =
VAR CurrentYear =
    MAX(curated_energy[year])
VAR CurrentValue =
    CALCULATE(
        [Electricity Demand TWh],
        curated_energy[year] = CurrentYear
    )
VAR PreviousValue =
    CALCULATE(
        [Electricity Demand TWh],
        curated_energy[year] = CurrentYear - 1
    )
RETURN
    DIVIDE(CurrentValue - PreviousValue, PreviousValue)
```

Keep the dashboard analytical and source-transparent. Do not imply that the data are Rystad proprietary.
