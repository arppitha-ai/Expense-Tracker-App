"""Step 2 - Data cleaning and feature engineering."""
import pandas as pd

CATEGORY_ALIASES = {"Eating Out": "Food", "Groceries": "Food", "Cab": "Transport"}
VALID_TYPES = {"Income", "Expense"}
WEEKDAY_ORDER = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


def add_features(df: pd.DataFrame) -> pd.DataFrame:
    """Create time-based columns used by analysis and charts."""
    df = df.copy()
    df["Year"] = df["Date"].dt.year
    df["Month"] = df["Date"].dt.to_period("M").astype(str)      # e.g. 2025-03 (sorts correctly)
    df["Month_Name"] = df["Date"].dt.month_name()
    df["Quarter"] = "Q" + df["Date"].dt.quarter.astype(str)
    df["Weekday"] = df["Date"].dt.day_name()
    df["Is_Weekend"] = df["Date"].dt.dayofweek >= 5
    return df


def clean_expenses(raw: pd.DataFrame):
    """Clean a raw transaction table. Returns (clean_df, report_dict)."""
    report = {"rows_raw": len(raw)}
    df = raw.copy()
    df.columns = df.columns.str.strip()

    # 1. duplicates
    before = len(df)
    df = df.drop_duplicates()
    report["duplicates_removed"] = before - len(df)

    # 2. text columns: trim spaces, consistent casing, alias mapping
    df["Category"] = df["Category"].fillna("Uncategorized").astype(str).str.strip().str.title()
    df["Category"] = df["Category"].replace(CATEGORY_ALIASES)
    df["Type"] = df["Type"].astype(str).str.strip().str.title()
    df["Payment_Method"] = df["Payment_Method"].fillna("Unknown").astype(str).str.strip()
    df["Description"] = df["Description"].fillna("").astype(str).str.strip()

    # 3. numeric / date conversion (invalid -> NaN/NaT instead of crashing)
    amount_text = df["Amount"].astype(str).str.replace(r"[^0-9.\-]", "", regex=True)
    df["Amount"] = pd.to_numeric(amount_text, errors="coerce")
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

    # 4. drop rows we cannot trust
    before = len(df)
    df = df.dropna(subset=["Date", "Amount"])
    df = df[(df["Amount"] > 0) & (df["Type"].isin(VALID_TYPES))]
    report["invalid_rows_removed"] = before - len(df)

    # 5. features
    df = add_features(df).sort_values("Date").reset_index(drop=True)
    report["rows_clean"] = len(df)
    report["uncategorized_rows"] = int((df["Category"] == "Uncategorized").sum())
    return df, report


def load_clean(path) -> pd.DataFrame:
    return pd.read_csv(path, parse_dates=["Date"])
