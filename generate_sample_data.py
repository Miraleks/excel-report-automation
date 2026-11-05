import csv
import random
from datetime import date, timedelta
from pathlib import Path

random.seed(42)

CITIES = ["Köln", "Bonn", "Berlin", "Hamburg", "München"]
CUSTOMERS = ["Müller GmbH", "Schmidt Logistik", "Weber & Söhne",
             "Fischer Trans", "Becker Handel", "Hoffmann KG"]


def messy_city(city: str) -> str:
    return random.choice([city, city.lower(), city.upper(), f" {city} "])


rows = []
start = date(2026, 1, 1)
for i in range(1, 301):
    d = start + timedelta(days=random.randint(0, 180))
    date_str = d.strftime("%d.%m.%Y") if random.random() < 0.5 else d.isoformat()
    amount = round(random.uniform(80, 1500), 2)
    amount_str = str(amount).replace(".", ",") if random.random() < 0.5 else str(amount)
    weight_str = "" if random.random() < 0.05 else str(round(random.uniform(5, 800), 1))
    rows.append([f"A{i:04d}", date_str, random.choice(CUSTOMERS),
                 messy_city(random.choice(CITIES)), amount_str, weight_str])

rows[5][4] = "n/a"                      # broken amount
rows += random.sample(rows, 10)         # duplicates

Path("data").mkdir(exist_ok=True)
with open("data/sample_orders.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f, delimiter=";")
    writer.writerow(["order_id", "order_date", "customer", "city", "amount_eur", "weight_kg"])
    writer.writerows(rows)

print("Created: data/sample_orders.csv")