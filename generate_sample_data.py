import csv
import random
from datetime import date, timedelta
from pathlib import Path

CITIES = ["Köln", "Bonn", "Berlin", "Hamburg", "München"]
CUSTOMERS = ["Müller GmbH", "Schmidt Logistik", "Weber & Söhne",
             "Fischer Trans", "Becker Handel", "Hoffmann KG"]
HEADER = ["order_id", "order_date", "customer", "city", "amount_eur", "weight_kg"]


def messy_city(city: str, rng: random.Random) -> str:
    return rng.choice([city, city.lower(), city.upper(), f" {city} "])


def generate_rows(n: int = 300, duplicates: int = 10, seed: int = 42) -> list[list[str]]:
    rng = random.Random(seed)
    start = date(2026, 1, 1)
    rows = []
    for i in range(1, n + 1):
        d = start + timedelta(days=rng.randint(0, 180))
        date_str = d.strftime("%d.%m.%Y") if rng.random() < 0.5 else d.isoformat()
        amount = round(rng.uniform(80, 1500), 2)
        amount_str = str(amount).replace(".", ",") if rng.random() < 0.5 else str(amount)
        weight_str = "" if rng.random() < 0.05 else str(round(rng.uniform(5, 800), 1))
        rows.append([f"A{i:04d}", date_str, rng.choice(CUSTOMERS),
                     messy_city(rng.choice(CITIES), rng), amount_str, weight_str])

    rows[5][4] = "n/a"                       # broken amount
    rows += rng.sample(rows, duplicates)     # duplicates
    return rows


def write_csv(path: Path, rows: list[list[str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f, delimiter=";")
        writer.writerow(HEADER)
        writer.writerows(rows)


def main() -> None:
    out = Path("data/sample_orders.csv")
    write_csv(out, generate_rows())
    print(f"Created {out}")


if __name__ == "__main__":
    main()