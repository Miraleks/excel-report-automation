# Excel Report Automation

A small Python tool that turns messy order exports (CSV) into a clean, ready-to-use Excel report in a single command.

Typical use case: a logistics or trading company exports orders from its system with inconsistent dates, decimal commas, duplicated rows and sloppy city names. This tool cleans the data and builds a summary workbook automatically, so nobody has to do it by hand in Excel every week.

## What it does

- Reads a semicolon-separated CSV file of orders
- Removes duplicate orders (by `order_id`)
- Normalizes dates (`31.12.2026` and `2026-12-31` are both accepted)
- Converts decimal commas to numbers (`100,50` becomes `100.5`)
- Trims whitespace and fixes letter case in city names
- Moves invalid rows (broken dates or amounts) to a separate sheet instead of silently dropping them
- Builds an Excel report with:
  - **Monthly**: orders, revenue and average weight per month, plus a bar chart
  - **By city**: orders and revenue per city
  - **Top customers**: top 5 customers by revenue
  - **Rejected rows**: everything that could not be processed

## Tech stack

Python 3.12, pandas, openpyxl, pytest, Docker

## Quick start

```bash
git clone https://github.com/YOUR_USERNAME/excel-report-automation.git
cd excel-report-automation
python -m venv .venv
```

Activate the virtual environment:

```bash
# Windows (PowerShell)
.venv\Scripts\Activate.ps1

# macOS / Linux
source .venv/bin/activate
```

Install dependencies and run:

```bash
pip install -r requirements.txt
python generate_sample_data.py
python report.py data/sample_orders.csv
```

The report is saved to `data/report.xlsx`.

## Usage

```bash
python report.py INPUT_CSV [-o OUTPUT_XLSX]
```

| Argument | Description |
|----------|-------------|
| `INPUT_CSV` | Path to the input CSV (separator `;`) |
| `-o`, `--output` | Output Excel file (default: `data/report.xlsx`) |

Expected CSV columns: `order_id`, `order_date`, `customer`, `city`, `amount_eur`, `weight_kg`.

`generate_sample_data.py` creates a demo file with deliberately messy data (mixed date formats, duplicates, missing values) so you can try the tool right away.

## Run with Docker

```bash
docker build -t report-tool .
docker run --rm -v "$(pwd)/data:/app/data" report-tool data/sample_orders.csv
```

On Windows PowerShell use `${PWD}` instead of `$(pwd)`. The report appears in your local `data` folder.

## Tests

```bash
pip install -r requirements-dev.txt
pytest -v
```

The tests cover the sample data generator, data cleaning, aggregation and the end-to-end creation of the Excel file.

## Project structure

```
excel-report-automation/
├── generate_sample_data.py   # creates demo CSV with messy data
├── report.py                 # cleaning, aggregation, Excel export
├── tests/                    # pytest tests
├── data/                     # input and output files
├── Dockerfile
├── requirements.txt
└── requirements-dev.txt
```

## Need something similar?

I build data processing and reporting automation (Python, SQL, Docker, Airflow). Contact: YOUR_EMAIL

## License

See the [LICENSE](LICENSE) file.