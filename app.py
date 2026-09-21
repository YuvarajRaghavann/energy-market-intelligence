from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data" / "processed"
QUALITY = ROOT / "data" / "quality"

st.set_page_config(
    page_title="Energy Market Intelligence",
    page_icon="⚡",
    layout="wide",
)

st.title("Energy Market Intelligence & Forecasting")
st.caption(
    "Public-data research prototype using the Our World in Data Energy dataset. "
    "Not based on Rystad proprietary data."
)

curated_path = DATA / "curated_energy.csv"
forecast_path = DATA / "forecast.csv"
model_metrics_path = DATA / "forecast_model_metrics.csv"
quality_path = QUALITY / "quality_report.json"

if not curated_path.exists():
    st.error(
        "Processed data not found. Run:\n\n"
        "python -m src.pipeline --country \"India\" "
        "--indicator electricity_demand --horizon 3"
    )
    st.stop()

df = pd.read_csv(curated_path)
df["year"] = pd.to_numeric(df["year"], errors="coerce")
df = df.dropna(subset=["country", "year"])
df["year"] = df["year"].astype(int)

# ---------------- Sidebar ----------------
st.sidebar.header("Research Controls")

countries = sorted(df["country"].dropna().unique())
default_country = countries.index("India") if "India" in countries else 0

country = st.sidebar.selectbox(
    "Country / region",
    countries,
    index=default_country,
)

indicator_options = [
    c
    for c in [
        "electricity_demand",
        "electricity_generation",
        "primary_energy_consumption",
        "oil_consumption",
        "gas_consumption",
        "coal_consumption",
        "renewables_consumption",
        "oil_production",
        "gas_production",
        "coal_production",
    ]
    if c in df.columns
]

indicator = st.sidebar.selectbox(
    "Primary indicator",
    indicator_options,
    index=0,
)

unit_map = {
    "electricity_demand": "TWh",
    "electricity_generation": "TWh",
    "primary_energy_consumption": "TWh",
    "oil_consumption": "TWh",
    "gas_consumption": "TWh",
    "coal_consumption": "TWh",
    "renewables_consumption": "TWh",
    "oil_production": "TWh",
    "gas_production": "TWh",
    "coal_production": "TWh",
}

unit = unit_map.get(indicator, "")

country_df = (
    df[df["country"].eq(country)]
    .sort_values("year")
    .copy()
)

country_indicator = (
    country_df[["year", indicator]]
    .dropna()
    .copy()
)

if country_indicator.empty:
    st.warning(f"No usable observations found for {country} and {indicator}.")
    st.stop()

latest = country_indicator.iloc[-1]
previous = (
    country_indicator.iloc[-2]
    if len(country_indicator) >= 2
    else None
)

latest_year = int(latest["year"])
latest_value = float(latest[indicator])

if previous is not None and float(previous[indicator]) != 0:
    yoy_pct = (
        latest_value / float(previous[indicator]) - 1
    ) * 100
else:
    yoy_pct = None

# ---------------- Market overview ----------------
st.header("Market Overview")

c1, c2, c3, c4 = st.columns(4)

c1.metric("Latest year", f"{latest_year}")
c2.metric(
    indicator.replace("_", " ").title(),
    f"{latest_value:,.1f} {unit}".strip(),
)
c3.metric(
    "YoY change",
    f"{yoy_pct:.2f}%" if yoy_pct is not None else "n/a",
)
c4.metric("Observations", f"{len(country_indicator):,}")

# ---------------- Historical trend ----------------
st.subheader(
    f"{country}: {indicator.replace('_', ' ').title()} over time"
)

fig = px.line(
    country_indicator,
    x="year",
    y=indicator,
    markers=True,
    labels={
        "year": "Year",
        indicator: f"{indicator.replace('_', ' ').title()} ({unit})".strip(),
    },
)

fig.update_layout(
    margin=dict(l=10, r=10, t=35, b=10),
)

st.plotly_chart(fig, width="stretch")

# ---------------- Recent analytical indicators ----------------
st.header("Recent Analytical Indicators")

analysis = country_df.copy()

if "electricity_demand" in analysis.columns:
    analysis["electricity_demand_yoy_pct"] = (
        analysis["electricity_demand"].pct_change() * 100
    )

if "primary_energy_consumption" in analysis.columns:
    analysis["primary_energy_yoy_pct"] = (
        analysis["primary_energy_consumption"].pct_change() * 100
    )

recent_columns = ["year"]

for col in [
    "electricity_demand_yoy_pct",
    "primary_energy_yoy_pct",
    "renewables_share_elec",
    "fossil_share_elec",
]:
    if col in analysis.columns:
        recent_columns.append(col)

recent = (
    analysis[recent_columns]
    .dropna(how="all", subset=recent_columns[1:])
    .tail(8)
)

if not recent.empty:
    renamed = recent.rename(
        columns={
            "electricity_demand_yoy_pct": "Electricity Demand YoY (%)",
            "primary_energy_yoy_pct": "Primary Energy YoY (%)",
            "renewables_share_elec": "Renewables Electricity Share (%)",
            "fossil_share_elec": "Fossil Electricity Share (%)",
        }
    )

    st.dataframe(
        renamed.round(2),
        width="stretch",
        hide_index=True,
    )
else:
    st.info("Not enough data for the recent indicators table.")

# ---------------- Energy mix ----------------
st.header("Energy Mix")

mix_cols = [
    c
    for c in ["fossil_share_elec", "renewables_share_elec"]
    if c in country_df.columns
]

if mix_cols:
    mix = country_df[["year"] + mix_cols].dropna(
        how="all",
        subset=mix_cols,
    )

    long_mix = mix.melt(
        id_vars="year",
        var_name="metric",
        value_name="share_pct",
    )

    fig_mix = px.line(
        long_mix,
        x="year",
        y="share_pct",
        color="metric",
        markers=True,
        labels={
            "year": "Year",
            "share_pct": "Electricity share (%)",
            "metric": "Metric",
        },
    )

    fig_mix.update_layout(
        margin=dict(l=10, r=10, t=35, b=10),
    )

    st.plotly_chart(fig_mix, width="stretch")

else:
    st.info(
        "Electricity-mix indicators are not available "
        "for the selected geography."
    )

# ---------------- Supply & consumption ----------------
st.header("Supply & Consumption")

supply_cols = [
    c
    for c in [
        "oil_production",
        "gas_production",
        "coal_production",
        "oil_consumption",
        "gas_consumption",
        "coal_consumption",
    ]
    if c in country_df.columns
]

if supply_cols:
    selected_supply = st.multiselect(
        "Select indicators",
        supply_cols,
        default=supply_cols[: min(4, len(supply_cols))],
    )

    if selected_supply:
        supply = country_df[["year"] + selected_supply].copy()

        supply_long = supply.melt(
            id_vars="year",
            var_name="metric",
            value_name="twh",
        ).dropna()

        fig_supply = px.line(
            supply_long,
            x="year",
            y="twh",
            color="metric",
            labels={
                "year": "Year",
                "twh": "TWh",
                "metric": "Indicator",
            },
        )

        fig_supply.update_layout(
            margin=dict(l=10, r=10, t=35, b=10),
        )

        st.plotly_chart(fig_supply, width="stretch")
    else:
        st.info("Select at least one indicator.")
else:
    st.info(
        "Supply/consumption indicators are not available "
        "for the selected geography."
    )

# ---------------- Forecast ----------------
st.header("Forecast & Model Evaluation")

model_metrics = None
if model_metrics_path.exists():
    model_metrics = pd.read_csv(model_metrics_path)

if model_metrics is not None and not model_metrics.empty:
    display_metrics = model_metrics.copy()

    model_labels = {
        "linear_regression": "Linear Regression",
        "naive_last_value": "Naive Baseline",
        "random_forest": "Random Forest",
    }

    display_metrics["model"] = display_metrics["model"].map(
        model_labels
    ).fillna(display_metrics["model"])

    display_metrics["mae_mean"] = (
        display_metrics["mae_mean"].round(2)
    )
    display_metrics["rmse_mean"] = (
        display_metrics["rmse_mean"].round(2)
    )

    display_metrics = display_metrics.rename(
        columns={
            "model": "Model",
            "mae_mean": "Mean CV MAE (TWh)",
            "rmse_mean": "Mean CV RMSE (TWh)",
            "folds": "Validation Folds",
        }
    )

    st.markdown(
        "The forecasting experiment compares a naive baseline, "
        "Linear Regression, and Random Forest using 4-fold "
        "time-series cross-validation. Error metrics are reported "
        "in TWh because electricity demand is measured in TWh."
    )

    st.dataframe(
        display_metrics,
        width="stretch",
        hide_index=True,
    )

    chart_metrics = model_metrics.copy()
    chart_metrics["model"] = chart_metrics["model"].map(
        model_labels
    ).fillna(chart_metrics["model"])

    fig_models = px.bar(
        chart_metrics.sort_values("mae_mean"),
        x="model",
        y="mae_mean",
        text_auto=".2f",
        labels={
            "model": "Model",
            "mae_mean": "Mean Cross-Validation MAE (TWh)",
        },
        title="Forecasting model comparison",
    )

    fig_models.update_layout(
        margin=dict(l=10, r=10, t=50, b=10),
    )

    st.plotly_chart(fig_models, width="stretch")

    best_model = model_metrics.sort_values(
        "mae_mean"
    ).iloc[0]

    a, b, c = st.columns(3)

    a.metric(
        "Selected by MAE",
        str(best_model["model"]),
    )

    b.metric(
        "Mean CV MAE",
        f"{best_model['mae_mean']:.2f}",
    )

    c.metric(
        "Mean CV RMSE",
        f"{best_model['rmse_mean']:.2f}",
    )

    st.caption(
        "MAE and RMSE are reported in the same unit as the forecast "
        "target. They are error metrics, not accuracy percentages."
    )

if forecast_path.exists():
    forecast = pd.read_csv(forecast_path)

    forecast_country = forecast[
        forecast["country"].eq(country)
    ].copy()

    if not forecast_country.empty:
        st.subheader(f"Saved forecast for {country}")

        shown_forecast = forecast_country.copy()
        shown_forecast["prediction"] = (
            shown_forecast["prediction"].round(2)
        )

        st.dataframe(
            shown_forecast,
            width="stretch",
            hide_index=True,
        )

        historical = country_indicator.rename(
            columns={indicator: "value"}
        ).copy()

        historical["series"] = "Actual"

        future = forecast_country[
            ["year", "prediction", "model"]
        ].copy()

        future = future.rename(
            columns={"prediction": "value"}
        )
        future["series"] = "Forecast"

        chart_data = pd.concat(
            [
                historical[["year", "value", "series"]],
                future[["year", "value", "series"]],
            ],
            ignore_index=True,
        )

        fig_forecast = px.line(
            chart_data,
            x="year",
            y="value",
            color="series",
            markers=True,
            labels={
                "year": "Year",
                "value": f"{indicator.replace('_', ' ').title()} ({unit})".strip(),
                "series": "",
            },
            title=f"{country}: actual vs forecast",
        )

        fig_forecast.update_layout(
            margin=dict(l=10, r=10, t=50, b=10),
        )

        st.plotly_chart(
            fig_forecast,
            width="stretch",
        )

    else:
        st.info(
            "The saved forecast was generated for another country. "
            "Rerun the pipeline for this country to generate a new forecast."
        )

else:
    st.info("No saved forecast was found.")

# ---------------- Research notes ----------------
st.header("Research Notes")

notes = []

if "electricity_demand" in country_df.columns:
    ed = (
        country_df[
            ["year", "electricity_demand"]
        ]
        .dropna()
        .sort_values("year")
    )

    if len(ed) >= 5:
        start = float(ed.iloc[-5]["electricity_demand"])
        end = float(ed.iloc[-1]["electricity_demand"])

        if start > 0:
            cagr = (
                (end / start) ** (1 / 4) - 1
            ) * 100

            notes.append(
                f"Electricity demand CAGR over the latest four-year "
                f"interval: {cagr:.2f}%."
            )

if "renewables_share_elec" in country_df.columns:
    renew = (
        country_df[
            ["year", "renewables_share_elec"]
        ]
        .dropna()
        .sort_values("year")
    )

    if len(renew) >= 2:
        delta = float(
            renew.iloc[-1]["renewables_share_elec"]
            - renew.iloc[-2]["renewables_share_elec"]
        )

        notes.append(
            "Renewables' electricity share changed by "
            f"{delta:+.2f} percentage points in the latest "
            "year-to-year comparison."
        )

if "fossil_share_elec" in country_df.columns:
    fossil = (
        country_df[
            ["year", "fossil_share_elec"]
        ]
        .dropna()
        .sort_values("year")
    )

    if len(fossil) >= 2:
        delta = float(
            fossil.iloc[-1]["fossil_share_elec"]
            - fossil.iloc[-2]["fossil_share_elec"]
        )

        notes.append(
            "Fossil electricity share changed by "
            f"{delta:+.2f} percentage points in the latest "
            "year-to-year comparison."
        )

if notes:
    for note in notes:
        st.write("• " + note)
else:
    st.info(
        "Additional research notes require more complete indicators."
    )

# ---------------- Data quality ----------------
st.header("Data Quality")

if quality_path.exists():
    report = json.loads(
        quality_path.read_text(encoding="utf-8")
    )

    q1, q2, q3, q4 = st.columns(4)

    q1.metric(
        "Rows checked",
        f"{report.get('row_count', 0):,}",
    )

    q2.metric(
        "Columns",
        f"{report.get('column_count', 0):,}",
    )

    q3.metric(
        "Duplicate country-year rows",
        f"{report.get('duplicate_country_year_rows', 0):,}",
    )

    q4.metric(
        "Quality check",
        "PASS" if report.get("quality_pass") else "REVIEW",
    )

    with st.expander("Detailed data-quality checks"):
        missingness = report.get("missingness", {})
        if missingness:
            missing_df = (
                pd.DataFrame.from_dict(missingness, orient="index")
                .reset_index()
                .rename(columns={"index": "Column", "count": "Missing Values", "rate": "Missing Rate"})
            )
            missing_df["Missing Rate"] = (missing_df["Missing Rate"] * 100).round(2).astype(str) + "%"
            st.write("**Missingness**")
            st.dataframe(missing_df, width="stretch", hide_index=True)
        else:
            st.success("No missing values were reported in the quality-check scan.")

        negative_values = report.get("negative_values", {})
        negative_df = pd.DataFrame(
            [(k, v) for k, v in negative_values.items()],
            columns=["Indicator", "Negative Values"],
        )
        st.write("**Negative-value checks**")
        st.dataframe(negative_df, width="stretch", hide_index=True)

        gap = report.get("annual_gap_checks", {})
        gap_df = pd.DataFrame(
            [
                ["Rows with year gaps", gap.get("rows_with_year_gap", 0)],
                ["Countries with year gaps", gap.get("countries_with_year_gaps", 0)],
            ],
            columns=["Check", "Result"],
        )
        st.write("**Annual observation gaps**")
        st.dataframe(gap_df, width="stretch", hide_index=True)

        outliers = report.get("potential_outliers_iqr", {})
        outlier_df = pd.DataFrame(
            [(k, v) for k, v in outliers.items()],
            columns=["Indicator", "Potential IQR Outliers"],
        )
        st.write("**Potential IQR outliers**")
        st.dataframe(outlier_df, width="stretch", hide_index=True)

else:
    st.info("No quality report found.")

# ---------------- Methodology ----------------
st.header("Methodology & Sources")

st.write(
    "Primary data source: Our World in Data Energy dataset. "
    "The dataset is organized by location and year and documents "
    "underlying source families including the Energy Institute, "
    "U.S. Energy Information Administration and Ember."
)

st.markdown(
    "- OWID Energy dataset: https://github.com/owid/energy-data\n"
    "- OWID codebook: https://github.com/owid/energy-data/blob/master/owid-energy-codebook.csv\n"
    "- IEA World Energy Statistics: https://www.iea.org/data-and-statistics/data-product/world-energy-statistics"
)

st.caption(
    "Forecasts are research prototypes based on historical public data. "
    "They should not be interpreted as investment, commodity-price, "
    "or market-advice forecasts."
)
