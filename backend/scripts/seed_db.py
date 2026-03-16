import asyncio
import csv
from pathlib import Path

from sqlalchemy import insert, text

from backend.config import settings
from backend.database import engine, Base
from backend.models.property import Property

DATA_FILE = Path(settings.csv_path)

COL_MAP = {
    "PROPERTY TYPE": "property_type",
    "ADDRESS": "address",
    "CITY": "city",
    "STATE OR PROVINCE": "state",
    "ZIP OR POSTAL CODE": "zip_code",
    "PRICE": "price",
    "BEDS": "beds",
    "BATHS": "baths",
    "LOCATION": "neighborhood",
    "SQUARE FEET": "sqft",
    "LOT SIZE": "lot_size",
    "YEAR BUILT": "year_built",
    "DAYS ON MARKET": "days_on_market",
    "HOA/MONTH": "hoa_month",
    "STATUS": "listing_status",
    "LATITUDE": "latitude",
    "LONGITUDE": "longitude",
    "URL (SEE https://www.redfin.com/buy-a-home/comparative-market-analysis FOR INFO ON PRICING)": "url",
}

INT_COLS = {"price", "beds", "sqft", "lot_size", "year_built", "days_on_market"}
FLOAT_COLS = {"baths", "hoa_month", "latitude", "longitude"}


def _coerce(col: str, val: str):
    if val == "":
        return None
    if col in INT_COLS:
        try:
            return int(float(val))
        except ValueError:
            return None
    if col in FLOAT_COLS:
        try:
            return float(val)
        except ValueError:
            return None
    return val


async def seed():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        await conn.execute(text("TRUNCATE TABLE properties RESTART IDENTITY"))

    rows = []
    with open(DATA_FILE, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for raw in reader:
            row = {db_col: _coerce(db_col, raw[csv_col])
                   for csv_col, db_col in COL_MAP.items()
                   if csv_col in raw}
            rows.append(row)

    batch_size = 500
    async with engine.begin() as conn:
        for i in range(0, len(rows), batch_size):
            await conn.execute(insert(Property), rows[i:i + batch_size])

    print(f"Seeded {len(rows)} properties")


if __name__ == "__main__":
    asyncio.run(seed())
