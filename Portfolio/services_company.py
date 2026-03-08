import csv
from .models import Stock

def import_company_master(csv_path):
    created = 0
    updated = 0

    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            ticker = (row.get("ticker") or "").strip().upper()
            name = (row.get("name") or "").strip() or None
            sector = (row.get("sector") or "").strip() or None

            if not ticker:
                continue

            _, was_created = Stock.objects.update_or_create(
                ticker=ticker,
                defaults={"name": name, "sector": sector},
            )
            if was_created:
                created += 1
            else:
                updated += 1

    return {"created": created, "updated": updated}