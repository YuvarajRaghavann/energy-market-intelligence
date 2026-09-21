from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "data" / "raw"
PROCESSED_DIR = ROOT / "data" / "processed"
QUALITY_DIR = ROOT / "data" / "quality"

OWID_URL = "https://owid-public.owid.io/data/energy/owid-energy-data.csv"

KEY_COLUMNS = ["country", "year"]

SELECTED_COLUMNS = [
    "country",
    "year",
    "iso_code",
    "population",
    "gdp",
    "primary_energy_consumption",
    "electricity_demand",
    "electricity_generation",
    "renewables_share_elec",
    "fossil_share_elec",
    "oil_consumption",
    "gas_consumption",
    "coal_consumption",
    "renewables_consumption",
    "oil_production",
    "gas_production",
    "coal_production",
    "solar_electricity",
    "wind_electricity",
    "hydro_electricity",
    "nuclear_electricity",
    "carbon_intensity_elec",
]

NON_NEGATIVE_COLUMNS = [
    "population",
    "gdp",
    "primary_energy_consumption",
    "electricity_demand",
    "electricity_generation",
    "oil_consumption",
    "gas_consumption",
    "coal_consumption",
    "renewables_consumption",
    "oil_production",
    "gas_production",
    "coal_production",
    "solar_electricity",
    "wind_electricity",
    "hydro_electricity",
    "nuclear_electricity",
]
