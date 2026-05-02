# Insight/services/benchmark_service.py

import pandas as pd
from datetime import datetime
from Insight.models import MarketBenchmark
from Portfolio.models import Portfolio, Holding, HistoricalPrice
def generate_benchmark_from_excel(file_path):
    xls = pd.ExcelFile(file_path)

    results = []

    for sheet in xls.sheet_names:
        df = pd.read_excel(xls, sheet_name=sheet)

        # convert numeric safely
        df["Close"] = pd.to_numeric(df["Close"], errors="coerce")
        df["Vol"] = pd.to_numeric(df["Vol"], errors="coerce")

        df = df.dropna(subset=["Close", "Vol"])

        if df.empty:
            continue

        # benchmark calculation (volume weighted index)
        benchmark_value = (df["Close"] * df["Vol"]).sum() / df["Vol"].sum()

        # FIX: convert 2026_02_28 → 2026-02-28
        clean_date = sheet.replace("_", "-")

        try:
            date_obj = datetime.strptime(clean_date, "%Y-%m-%d").date()
        except ValueError:
            # skip invalid sheet names
            continue

        results.append({
            "date": date_obj,
            "value": round(float(benchmark_value), 2)
        })

    # save to DB
    for item in results:
        MarketBenchmark.objects.update_or_create(
            date=item["date"],
            defaults={"value": item["value"]}
        )

    return results


