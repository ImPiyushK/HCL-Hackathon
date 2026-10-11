"""
Data Loader Utility (Section 4.7 & Annex B).
Loads CSV files into the DuckDB database with schema validation.
Can be executed as a CLI command or invoked programmatically by API endpoints.
"""

import os
import sys
import io
import argparse
from typing import Dict, Any, Tuple
import pandas as pd

# Add repo root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.database import db

REQUIRED_COLUMNS = {
    "meter_15min": ["meter_id", "ts", "kwh"],
    "tariff": ["valid_from", "valid_to", "period", "price_per_kwh"],
    "production": ["date", "product", "units", "shift_pattern", "is_holiday"],
    "weather": ["date", "avg_temp_c", "cooling_degree_days", "heating_degree_days"]
}

def load_csv(table_name: str, file_source, replace: bool = True) -> Tuple[int, int, str]:
    """
    Loads a CSV file into the specified table.
    file_source can be a filepath (str) or file-like object (bytes / StringIO).
    Returns (rows_loaded, rows_rejected, status_message).
    """
    if table_name not in REQUIRED_COLUMNS:
        return 0, 0, f"Unknown table '{table_name}'. Expected one of {list(REQUIRED_COLUMNS.keys())}"

    try:
        if isinstance(file_source, bytes):
            df = pd.read_csv(io.BytesIO(file_source))
        elif isinstance(file_source, str) and os.path.isfile(file_source):
            df = pd.read_csv(file_source)
        elif hasattr(file_source, "read"):
            df = pd.read_csv(file_source)
        else:
            return 0, 0, f"Invalid file source provided for {table_name}"
    except Exception as e:
        return 0, 0, f"Failed to parse CSV: {str(e)}"

    # Validate required columns
    req_cols = REQUIRED_COLUMNS[table_name]
    missing = [c for c in req_cols if c not in df.columns]
    if missing:
        return 0, len(df), f"Missing required columns for {table_name}: {missing}"

    initial_len = len(df)
    # Basic data cleaning: drop NaN rows in key columns
    df_clean = df.dropna(subset=req_cols).copy()
    rows_rejected = initial_len - len(df_clean)

    try:
        rows_loaded = db.load_table_from_df(table_name, df_clean, replace=replace)
        return len(df_clean), rows_rejected, "ok"
    except Exception as e:
        return 0, initial_len, f"Database insertion error: {str(e)}"

def load_all_from_directory(data_dir: str, replace: bool = True) -> Dict[str, Any]:
    """Loads all 4 standard tables from a folder."""
    results = {}
    for table_name in REQUIRED_COLUMNS.keys():
        csv_path = os.path.join(data_dir, f"{table_name}.csv")
        if os.path.exists(csv_path):
            loaded, rejected, status = load_csv(table_name, csv_path, replace=replace)
            results[table_name] = {
                "rows_loaded": loaded,
                "rows_rejected": rejected,
                "status": status
            }
        else:
            results[table_name] = {
                "rows_loaded": 0,
                "rows_rejected": 0,
                "status": f"File not found: {csv_path}"
            }
    return results

def main():
    parser = argparse.ArgumentParser(description="Annex B Factory Energy Data Loader CLI")
    parser.add_argument("--dir", default=os.path.dirname(os.path.abspath(__file__)),
                        help="Directory containing CSV files (default: data/)")
    parser.add_argument("--table", choices=list(REQUIRED_COLUMNS.keys()),
                        help="Specific table name to load")
    parser.add_argument("--file", help="Specific CSV file path to load")
    parser.add_argument("--append", action="store_true", help="Append data instead of replacing table")
    args = parser.parse_args()

    replace = not args.append

    if args.table and args.file:
        loaded, rejected, status = load_csv(args.table, args.file, replace=replace)
        print(f"[{args.table}] Loaded: {loaded}, Rejected: {rejected}, Status: {status}")
    else:
        print(f"Loading all datasets from: {args.dir}")
        res = load_all_from_directory(args.dir, replace=replace)
        for tbl, info in res.items():
            print(f" * {tbl:12s}: Loaded {info['rows_loaded']:,} rows, Rejected {info['rows_rejected']}, Status: {info['status']}")

    counts = db.get_counts()
    print("\nCurrent Database State:")
    for tbl, count in counts.items():
        print(f" - {tbl:12s}: {count:,} rows")

if __name__ == "__main__":
    main()
