import argparse
from pathlib import Path

import pandas as pd
from openpyxl.chart import BarChart, Reference
from openpyxl.styles import Font


def parse_dates(series: pd.Series) -> pd.Series:
    """Handle both 31.12.2026 and 2026-12-31."""
    german = pd.to_datetime(series, format="%d.%m.%Y", errors="coerce")
    iso = pd.to_datetime(series, format="%Y-%m-%d", errors="coerce")
    return german.fillna(iso)


def clean(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    df = df.copy()
    df.columns = df.columns.str.strip().str.lower()
    df = df.drop_duplicates(subset="order_id")

    df["customer"] = df["customer"].str.strip()
    df["city"] = df["city"].str.strip().str.title()
    df["order_date"] = parse_dates(df["order_date"].str.strip())
    for col in ("amount_eur", "weight_kg"):
        df[col] = pd.to_numeric(df[col].str.replace(",", ".", regex=False), errors="coerce")

    invalid = df["order_date"].isna() | df["amount_eur"].isna()
    return df[~invalid].copy(), df[invalid].copy()


def summarize(df: pd.DataFrame) -> dict[str, pd.DataFrame]:
    df["month"] = df["order_date"].dt.to_period("M").astype(str)
    monthly = (df.groupby("month")
                 .agg(orders=("order_id", "count"),
                      revenue=("amount_eur", "sum"),
                      avg_weight_kg=("weight_kg", "mean"))
                 .round(2).reset_index())
    by_city = (df.groupby("city")
                 .agg(orders=("order_id", "count"), revenue=("amount_eur", "sum"))
                 .sort_values("revenue", ascending=False)
                 .round(2).reset_index())
    top_customers = (df.groupby("customer")["amount_eur"].sum()
                       .nlargest(5).round(2).reset_index())
    return {"Monthly": monthly, "By city": by_city, "Top customers": top_customers}


def write_excel(sheets: dict[str, pd.DataFrame], rejected: pd.DataFrame, out: Path) -> None:
    with pd.ExcelWriter(out, engine="openpyxl") as writer:
        for name, data in sheets.items():
            data.to_excel(writer, sheet_name=name, index=False)
        rejected.to_excel(writer, sheet_name="Rejected rows", index=False)

        for ws in writer.book.worksheets:
            for cell in ws[1]:
                cell.font = Font(bold=True)
            for col in ws.columns:
                width = max(len(str(c.value)) if c.value is not None else 0 for c in col)
                ws.column_dimensions[col[0].column_letter].width = width + 2

        ws = writer.sheets["Monthly"]
        n = len(sheets["Monthly"])
        chart = BarChart()
        chart.title = "Revenue by month (EUR)"
        chart.add_data(Reference(ws, min_col=3, min_row=1, max_row=n + 1), titles_from_data=True)
        chart.set_categories(Reference(ws, min_col=1, min_row=2, max_row=n + 1))
        ws.add_chart(chart, "G2")


def main() -> None:
    parser = argparse.ArgumentParser(description="Clean order CSV and build an Excel report.")
    parser.add_argument("input", type=Path, help="path to the CSV file (separator ';')")
    parser.add_argument("-o", "--output", type=Path, default=Path("data/report.xlsx"))
    args = parser.parse_args()

    raw = pd.read_csv(args.input, sep=";", dtype=str)
    clean_df, rejected = clean(raw)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    write_excel(summarize(clean_df), rejected, args.output)
    write_excel(summarize(clean_df), rejected, args.output)
    print(f"Rows total: {len(raw)} | valid: {len(clean_df)} | rejected: {len(rejected)}")
    print(f"Report saved to {args.output}")


if __name__ == "__main__":
    main()