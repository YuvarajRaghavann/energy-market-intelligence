CREATE TABLE IF NOT EXISTS dim_geography (
    country TEXT PRIMARY KEY,
    iso_code CHAR(3)
);

CREATE TABLE IF NOT EXISTS fact_energy_annual (
    country TEXT NOT NULL REFERENCES dim_geography(country),
    year INTEGER NOT NULL,
    population DOUBLE PRECISION,
    gdp DOUBLE PRECISION,
    primary_energy_consumption DOUBLE PRECISION,
    electricity_demand DOUBLE PRECISION,
    electricity_generation DOUBLE PRECISION,
    renewables_share_elec DOUBLE PRECISION,
    fossil_share_elec DOUBLE PRECISION,
    oil_consumption DOUBLE PRECISION,
    gas_consumption DOUBLE PRECISION,
    coal_consumption DOUBLE PRECISION,
    renewables_consumption DOUBLE PRECISION,
    oil_production DOUBLE PRECISION,
    gas_production DOUBLE PRECISION,
    coal_production DOUBLE PRECISION,
    solar_electricity DOUBLE PRECISION,
    wind_electricity DOUBLE PRECISION,
    hydro_electricity DOUBLE PRECISION,
    nuclear_electricity DOUBLE PRECISION,
    carbon_intensity_elec DOUBLE PRECISION,
    PRIMARY KEY (country, year)
);

CREATE TABLE IF NOT EXISTS fact_market_metrics (
    country TEXT PRIMARY KEY REFERENCES dim_geography(country),
    latest_year INTEGER,
    latest_electricity_demand_twh DOUBLE PRECISION,
    latest_primary_energy_twh DOUBLE PRECISION,
    latest_renewables_share_elec_pct DOUBLE PRECISION,
    latest_fossil_share_elec_pct DOUBLE PRECISION,
    electricity_demand_3y_cagr_pct DOUBLE PRECISION,
    electricity_demand_5y_cagr_pct DOUBLE PRECISION
);

CREATE TABLE IF NOT EXISTS fact_forecast (
    country TEXT NOT NULL REFERENCES dim_geography(country),
    indicator TEXT NOT NULL,
    year INTEGER NOT NULL,
    prediction DOUBLE PRECISION,
    model TEXT NOT NULL,
    PRIMARY KEY (country, indicator, year)
);

CREATE TABLE IF NOT EXISTS fact_data_quality (
    check_name TEXT PRIMARY KEY,
    check_value JSONB NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_energy_country_year
    ON fact_energy_annual(country, year);
