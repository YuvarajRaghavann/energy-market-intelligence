import pandas as pd

from src.quality import run_quality_checks
from src.transform import add_derived_indicators, prepare_curated_dataset


def sample_df():
    rows = []
    for year in range(2015, 2025):
        rows.append(
            {
                "country": "Demo",
                "year": year,
                "iso_code": "DMM",
                "population": 10_000_000 + (year - 2015) * 100_000,
                "gdp": 100_000 + (year - 2015) * 5_000,
                "primary_energy_consumption": 1000 + (year - 2015) * 20,
                "electricity_demand": 500 + (year - 2015) * 10,
                "electricity_generation": 510 + (year - 2015) * 10,
                "renewables_share_elec": 20 + (year - 2015) * 1.0,
                "fossil_share_elec": 70 - (year - 2015) * 1.0,
                "oil_consumption": 300,
                "gas_consumption": 250,
                "coal_consumption": 250,
                "renewables_consumption": 200,
                "oil_production": 120,
                "gas_production": 100,
                "coal_production": 90,
                "solar_electricity": 20,
                "wind_electricity": 30,
                "hydro_electricity": 40,
                "nuclear_electricity": 10,
                "carbon_intensity_elec": 500,
            }
        )
    return pd.DataFrame(rows)


def test_quality_report_has_no_duplicate_keys():
    report = run_quality_checks(sample_df())
    assert report["duplicate_country_year_rows"] == 0


def test_transform_adds_yoy():
    curated = prepare_curated_dataset(sample_df())
    derived = add_derived_indicators(curated)
    assert "electricity_demand_yoy_pct" in derived.columns
    assert derived["electricity_demand_yoy_pct"].notna().sum() > 0
