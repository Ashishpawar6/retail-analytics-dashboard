"""Download the public UCI "Online Retail" dataset (no login needed)."""
import zipfile
from pathlib import Path

import requests

URL = "https://archive.ics.uci.edu/static/public/352/online+retail.zip"
RAW_DIR = Path("data/raw")
XLSX = RAW_DIR / "online_retail.xlsx"


def download(force: bool = False) -> Path:
    if XLSX.exists() and not force:
        return XLSX
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    zip_path = RAW_DIR / "online_retail.zip"
    response = requests.get(URL, timeout=120)
    response.raise_for_status()
    zip_path.write_bytes(response.content)
    with zipfile.ZipFile(zip_path) as zf:
        members = [m for m in zf.namelist() if m.lower().endswith(".xlsx") and ".." not in m]
        if len(members) != 1:
            raise RuntimeError(f"Expected one .xlsx in the archive, found {members}")
        XLSX.write_bytes(zf.read(members[0]))  # write to a fixed name, never to a path from the archive
    return XLSX
