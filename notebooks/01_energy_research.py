from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
path = ROOT / "data" / "processed" / "curated_energy.csv"

df = pd.read_csv(path)
country = "India"
g = df[df["country"].eq(country)].sort_values("year").copy()

g["electricity_demand_yoy_pct"] = g["electricity_demand"].pct_change() * 100

fig = plt.figure(figsize=(10, 5))
plt.plot(g["year"], g["electricity_demand"])
plt.xlabel("Year")
plt.ylabel("Electricity demand (TWh)")
plt.title(f"{country}: electricity demand")
plt.tight_layout()
plt.show()

fig = plt.figure(figsize=(10, 5))
plt.plot(g["year"], g["renewables_share_elec"], label="Renewables share")
plt.plot(g["year"], g["fossil_share_elec"], label="Fossil share")
plt.xlabel("Year")
plt.ylabel("Share of electricity (%)")
plt.title(f"{country}: electricity mix")
plt.legend()
plt.tight_layout()
plt.show()
