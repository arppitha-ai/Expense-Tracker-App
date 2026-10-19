"""Step 3 - Analysis: KPIs, category/monthly summaries, overspending, anomalies, forecast."""
import numpy as np
import pandas as pd

from .clean_data import WEEKDAY_ORDER
from .config import ANOMALY_Z_THRESHOLD, MONTHLY_BUDGETS


def expenses_only(df):
    return df[df["Type"] == "Expense"]


def kpis(df) -> dict:
    inc = df.loc[df["Type"] == "Income", "Amount"].sum()
    exp = df.loc[df["Type"] == "Expense", "Amount"].sum()
    return {
        "total_income": float(inc),
        "total_expense": float(exp),
        "net_savings": float(inc - exp),
        "savings_rate_pct": round(float((inc - exp) / inc * 100), 1) if inc else 0.0,
        "transactions": int(len(df)),
        "avg_expense_txn": round(float(df.loc[df["Type"] == "Expense", "Amount"].mean()), 1),
    }


def category_summary(df) -> pd.DataFrame:
    exp = expenses_only(df)
    out = (exp.groupby("Category")["Amount"]
              .agg(Total="sum", Transactions="count", Average="mean")
              .sort_values("Total", ascending=False))
    out["Share_%"] = (out["Total"] / out["Total"].sum() * 100).round(1)
    out["Average"] = out["Average"].round(0)
    return out.reset_index()


def group_small_categories(cat_df, min_share=4.0):
    """Merge categories below min_share % into one 'Other (small)' slice for cleaner pies."""
    small = cat_df["Share_%"] < min_share
    big = cat_df.loc[~small, ["Category", "Total"]]
    if small.sum() > 1:
        other = pd.DataFrame([{"Category": "Other (small)",
                               "Total": cat_df.loc[small, "Total"].sum()}])
        return pd.concat([big, other], ignore_index=True)
    return cat_df[["Category", "Total"]]


def monthly_summary(df) -> pd.DataFrame:
    pivot = df.pivot_table(index="Month", columns="Type", values="Amount",
                           aggfunc="sum", fill_value=0)
    for col in ("Income", "Expense"):
        if col not in pivot:
            pivot[col] = 0
    pivot["Savings"] = pivot["Income"] - pivot["Expense"]
    pivot["Savings_Rate_%"] = (pivot["Savings"] / pivot["Income"].replace(0, np.nan) * 100).round(1)
    return pivot[["Income", "Expense", "Savings", "Savings_Rate_%"]].reset_index()


def monthly_category_matrix(df) -> pd.DataFrame:
    return expenses_only(df).pivot_table(index="Month", columns="Category", values="Amount",
                                         aggfunc="sum", fill_value=0)


def weekday_pattern(df) -> pd.DataFrame:
    """Average total spend per calendar day, by weekday."""
    daily = expenses_only(df).groupby("Date")["Amount"].sum().reset_index()
    daily["Weekday"] = daily["Date"].dt.day_name()
    out = daily.groupby("Weekday")["Amount"].mean().reindex(WEEKDAY_ORDER).round(0)
    return out.rename("Avg_Daily_Spend").reset_index()


def payment_summary(df) -> pd.DataFrame:
    return (expenses_only(df).groupby("Payment_Method")["Amount"].sum()
            .sort_values(ascending=False).rename("Total").reset_index())


def budget_check(df, budgets=None) -> pd.DataFrame:
    """Overspending detection: every (month, category) where spend > monthly budget."""
    budgets = budgets or MONTHLY_BUDGETS
    matrix = monthly_category_matrix(df)
    rows = []
    for cat, budget in budgets.items():
        if cat not in matrix.columns:
            continue
        for month, spent in matrix[cat].items():
            if spent > budget:
                rows.append({"Month": month, "Category": cat, "Budget": budget,
                             "Spent": spent, "Overspend": spent - budget,
                             "Overspend_%": round((spent - budget) / budget * 100, 1)})
    cols = ["Month", "Category", "Budget", "Spent", "Overspend", "Overspend_%"]
    return (pd.DataFrame(rows, columns=cols)
              .sort_values(["Month", "Overspend"], ascending=[True, False])
              .reset_index(drop=True))


def detect_anomalies(df, z_threshold=ANOMALY_Z_THRESHOLD) -> pd.DataFrame:
    """Flag unusually large single transactions using a per-category z-score."""
    exp = expenses_only(df).copy()
    grp = exp.groupby("Category")["Amount"]
    exp["Z_Score"] = ((exp["Amount"] - grp.transform("mean")) / grp.transform("std")).round(2)
    out = exp[exp["Z_Score"] > z_threshold]
    return (out[["Date", "Category", "Description", "Amount", "Z_Score"]]
            .sort_values("Amount", ascending=False).reset_index(drop=True))


def forecast_next_month(monthly: pd.DataFrame) -> dict:
    """Very simple baseline forecast (3-month average + linear trend)."""
    y = monthly["Expense"].to_numpy(dtype=float)
    x = np.arange(len(y))
    slope, intercept = np.polyfit(x, y, 1)
    trend = slope * len(y) + intercept
    sma = y[-3:].mean()
    return {"moving_avg_3m": round(sma), "linear_trend": round(trend),
            "blended": round((sma + trend) / 2)}