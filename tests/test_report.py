import sys

import pandas as pd
import pytest
from openpyxl import load_workbook

import report
from generate_sample_data import HEADER, generate_rows, write_csv


def make_df() -> pd.DataFrame:
    rows = [
        ["A1", "01.02.2026", "Müller GmbH", " köln ", "100,50", "10.5"],
        ["A1", "01.02.2026", "Müller GmbH", " köln ", "100,50", "10.5"],  # duplicate
        ["A2", "2026-02-03", "Müller GmbH", "BONN", "200", ""],
        ["A3", "2026-02-04", "Müller GmbH", "Bonn", "n/a", "5"],          # bad amount
        ["A4", "not a date", "Müller GmbH", "Bonn", "50", "5"],           # bad date
    ]
    return pd.DataFrame(rows, columns=HEADER, dtype=str)


def test_parse_dates_both_formats():
    result = report.parse_dates(pd.Series(["31.12.2026", "2026-12-31", "garbage"]))
    assert result.iloc[0] == pd.Timestamp("2026-12-31")
    assert result.iloc[1] == pd.Timestamp("2026-12-31")
    assert pd.isna(result.iloc[2])


def test_clean_normalizes_and_rejects():
    valid, rejected = report.clean(make_df())

    assert list(valid["order_id"]) == ["A1", "A2"]
    assert set(valid["city"]) == {"Köln", "Bonn"}
    assert valid.loc[valid["order_id"] == "A1", "amount_eur"].iloc[0] == 100.5
    assert list(rejected["order_id"]) == ["A3", "A4"]


def test_summarize_totals():
    valid, _ = report.clean(make_df())
    result = report.summarize(valid)

    assert set(result) == {"Monthly", "By city", "Top customers"}
    monthly = result["Monthly"]
    assert monthly["orders"].sum() == 2
    assert monthly["revenue"].sum() == pytest.approx(300.5)


def test_main_creates_excel_report(tmp_path, monkeypatch):
    csv_path = tmp_path / "orders.csv"
    out_path = tmp_path / "out" / "report.xlsx"   # folder does not exist yet
    write_csv(csv_path, generate_rows())
    monkeypatch.setattr(sys, "argv", ["report.py", str(csv_path), "-o", str(out_path)])

    report.main()

    assert out_path.exists()
    wb = load_workbook(out_path)
    assert wb.sheetnames == ["Monthly", "By city", "Top customers", "Rejected rows"]