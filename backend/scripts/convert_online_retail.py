from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from app.services.dataset_adapters import convert_online_retail_dataframe


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT = PROJECT_ROOT / "data" / "processed" / "online_retail_sales.csv"


def read_dataset(path: Path) -> pd.DataFrame:
    if path.suffix.lower() in {".xlsx", ".xls"}:
        return pd.read_excel(path)
    return pd.read_csv(path)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Convert an Online Retail CSV/XLSX dataset into the platform sales CSV schema."
    )
    parser.add_argument("--input", required=True, help="Path to Online Retail .csv, .xlsx, or .xls file")
    parser.add_argument(
        "--output",
        default=str(DEFAULT_OUTPUT),
        help=f"Output CSV path. Default: {DEFAULT_OUTPUT}",
    )
    parser.add_argument(
        "--max-rows",
        type=int,
        default=None,
        help="Optional maximum number of converted rows to write, useful for local demos.",
    )
    args = parser.parse_args()

    input_path = Path(args.input).resolve()
    output_path = Path(args.output).resolve()

    if not input_path.exists():
        raise FileNotFoundError(f"Input dataset not found: {input_path}")

    raw_df = read_dataset(input_path)
    converted_df = convert_online_retail_dataframe(raw_df)
    if args.max_rows is not None:
        converted_df = converted_df.head(args.max_rows)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    converted_df.to_csv(output_path, index=False)

    print(f"Converted rows: {len(converted_df):,}")
    print(f"Output: {output_path}")


if __name__ == "__main__":
    main()
