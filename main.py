"""Run the whole pipeline:  python main.py   (add --regen to rebuild the synthetic data)"""
import argparse

import matplotlib
matplotlib.use("Agg")  # save charts to files, no pop-up windows

from src import analysis as an
from src import insights, visualize
from src.clean_data import clean_expenses
from src.config import CLEAN_FILE, OUTPUT_DIR, RAW_FILE
from src.generate_data import create_raw_dataset

import pandas as pd


def main(regen=False, plots=True):
    OUTPUT_DIR.mkdir(exist_ok=True)

    print("STEP 1/5  Data creation")
    raw = create_raw_dataset() if (regen or not RAW_FILE.exists()) else pd.read_csv(RAW_FILE)
    print(f"  raw rows: {len(raw)}  ->  {RAW_FILE.name}")

    print("STEP 2/5  Cleaning")
    df, report = clean_expenses(raw)
    df.to_csv(CLEAN_FILE, index=False)
    for key, val in report.items():
        print(f"  {key}: {val}")

    print("STEP 3/5  Analysis")
    an.category_summary(df).to_csv(OUTPUT_DIR / "category_summary.csv", index=False)
    an.monthly_summary(df).to_csv(OUTPUT_DIR / "monthly_summary.csv", index=False)
    an.budget_check(df).to_csv(OUTPUT_DIR / "budget_alerts.csv", index=False)
    an.detect_anomalies(df).to_csv(OUTPUT_DIR / "anomalies.csv", index=False)
    print("  saved summaries to outputs/")

    if plots:
        print("STEP 4/5  Visualization")
        print(f"  saved {visualize.make_all(df)} charts to images/")

    print("STEP 5/5  Insights")
    for i, line in enumerate(insights.generate_insights(df), 1):
        print(f"  {i}. {line}")
    print(f"  report: {insights.write_report(df)}")
    print("\nDone. Launch the dashboard with:  streamlit run app.py")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--regen", action="store_true", help="regenerate synthetic raw data")
    ap.add_argument("--no-plots", action="store_true", help="skip chart generation")
    a = ap.parse_args()
    main(regen=a.regen, plots=not a.no_plots)
