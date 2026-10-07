import sqlite3
from pathlib import Path

import pandas as pd

SQL_DIR = Path(__file__).resolve().parent.parent / "sql"


def build_database(path: Path, tables: dict[str, pd.DataFrame]) -> None:
    """Write DataFrames as SQLite tables (replacing any existing database) and add indexes."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.unlink(missing_ok=True)
    with sqlite3.connect(path) as conn:
        for name, frame in tables.items():
            frame = frame.copy()
            for col in frame.columns:
                if pd.api.types.is_datetime64_any_dtype(frame[col]):
                    frame[col] = frame[col].dt.strftime("%Y-%m-%d %H:%M:%S")
            frame.to_sql(name, conn, index=False)
        conn.execute("CREATE INDEX idx_sales_month ON sales(invoice_month)")
        conn.execute("CREATE INDEX idx_sales_customer ON sales(customer_id)")
        conn.execute("CREATE INDEX idx_sales_country ON sales(country)")


def run_sql_file(conn: sqlite3.Connection, name: str) -> pd.DataFrame:
    """Run sql/<name>.sql and return the result as a DataFrame."""
    return pd.read_sql_query((SQL_DIR / f"{name}.sql").read_text(), conn)
