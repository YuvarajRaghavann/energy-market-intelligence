from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import requests

from .config import OWID_URL, RAW_DIR


def download_energy_data(output_path: Path | None = None) -> Path:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    output_path = output_path or (RAW_DIR / "owid-energy-data.csv")

    response = requests.get(
        OWID_URL,
        timeout=120,
        headers={"User-Agent": "energy-market-intelligence-project/1.0"},
    )
    response.raise_for_status()
    output_path.write_bytes(response.content)

    return output_path


def load_raw_data(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(
            f"Raw data not found at {path}. Run download_energy_data() first."
        )

    df = pd.read_csv(path)
    df["retrieved_at_utc"] = datetime.now(timezone.utc).isoformat()
    return df
