"""Step 4 - Charts. Every function saves a PNG into images/ and returns the figure."""
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

from . import analysis as an
from .config import IMAGE_DIR, MONTHLY_BUDGETS, TARGET_SAVINGS_RATE

sns.set_theme(style="whitegrid", context="notebook")
RUPEE = "\u20b9"


def _save(fig, name, save=True):
    if save:
        IMAGE_DIR.mkdir(parents=True, exist_ok=True)
        fig.savefig(IMAGE_DIR / name, dpi=150, bbox_inches="tight")
    return fig


def category_bar(df, save=True):
    cat = an.category_summary(df)
    fig, ax = plt.subplots(figsize=(10, 5))
    sns.barplot(data=cat, x="Category", y="Total", hue="Category", palette="Set2",
                legend=False, ax=ax)
    ax.set_title("Total Expense by Category")
    ax.set_ylabel(f"Total Spent ({RUPEE})")
    ax.tick_params(axis="x", rotation=45)
    for p in ax.patches:
        ax.annotate(f"{p.get_height():,.0f}", (p.get_x() + p.get_width() / 2, p.get_height()),
                    ha="center", va="bottom", fontsize=8)
    return _save(fig, "01_category_bar.png", save)


def expense_pie(df, save=True):
    pie = an.group_small_categories(an.category_summary(df))
    fig, ax = plt.subplots(figsize=(9, 7))
    ax.pie(pie["Total"], autopct="%1.1f%%", startangle=90, pctdistance=0.78,
           colors=sns.color_palette("Set3", len(pie)), wedgeprops=dict(width=0.45))
    ax.legend(pie["Category"], loc="center left", bbox_to_anchor=(1, 0.5), frameon=False)
    ax.set_title("Expense Distribution by Category")
    return _save(fig, "02_expense_pie.png", save)


def monthly_income_vs_expense(df, save=True):
    m = an.monthly_summary(df)
    fig, ax = plt.subplots(figsize=(11, 5))
    ax.plot(m["Month"], m["Income"], marker="o", label="Income", color="#2a9d8f")
    ax.plot(m["Month"], m["Expense"], marker="o", label="Expense", color="#e76f51")
    ax.fill_between(m["Month"], m["Expense"], m["Income"], alpha=0.12, color="#2a9d8f")
    ax.set_title("Monthly Income vs Expense")
    ax.set_ylabel(f"Amount ({RUPEE})")
    ax.tick_params(axis="x", rotation=45)
    ax.legend()
    return _save(fig, "03_monthly_income_vs_expense.png", save)


def savings_rate_chart(df, save=True):
    m = an.monthly_summary(df)
    colors = ["#2a9d8f" if v >= TARGET_SAVINGS_RATE else "#e76f51" for v in m["Savings_Rate_%"]]
    fig, ax = plt.subplots(figsize=(11, 5))
    ax.bar(m["Month"], m["Savings_Rate_%"], color=colors)
    ax.axhline(TARGET_SAVINGS_RATE, ls="--", color="gray", label=f"Target {TARGET_SAVINGS_RATE:.0f}%")
    ax.set_title("Monthly Savings Rate (%)")
    ax.set_ylabel("% of income saved")
    ax.tick_params(axis="x", rotation=45)
    ax.legend()
    return _save(fig, "04_savings_rate.png", save)


def weekday_chart(df, save=True):
    w = an.weekday_pattern(df)
    fig, ax = plt.subplots(figsize=(9, 4.5))
    sns.barplot(data=w, x="Weekday", y="Avg_Daily_Spend", hue="Weekday",
                palette="coolwarm", legend=False, ax=ax)
    ax.set_title("Average Daily Spend by Weekday (variable spending days)")
    ax.set_ylabel(f"Avg spend per day ({RUPEE})")
    return _save(fig, "05_weekday_spending.png", save)


def category_month_heatmap(df, save=True):
    mat = an.monthly_category_matrix(df)
    fig, ax = plt.subplots(figsize=(12, 6))
    sns.heatmap(mat, annot=True, fmt=".0f", cmap="YlOrRd", linewidths=0.5, ax=ax,
                cbar_kws={"label": f"Spend ({RUPEE})"})
    ax.set_title("Spending Heatmap: Month x Category")
    return _save(fig, "06_category_month_heatmap.png", save)


def payment_method_chart(df, save=True):
    p = an.payment_summary(df)
    fig, ax = plt.subplots(figsize=(7, 7))
    ax.pie(p["Total"], labels=p["Payment_Method"], autopct="%1.1f%%", startangle=90,
           wedgeprops=dict(width=0.45), colors=sns.color_palette("pastel"))
    ax.set_title("Spending by Payment Method")
    return _save(fig, "07_payment_methods.png", save)


def budget_vs_actual(df, save=True):
    mat = an.monthly_category_matrix(df)
    cats = [c for c in MONTHLY_BUDGETS if c in mat.columns]
    avg = mat[cats].mean()
    x = np.arange(len(cats))
    fig, ax = plt.subplots(figsize=(11, 5))
    ax.bar(x - 0.2, [MONTHLY_BUDGETS[c] for c in cats], 0.4, label="Monthly budget", color="#8ecae6")
    ax.bar(x + 0.2, avg.values, 0.4, label="Average actual", color="#fb8500")
    ax.set_xticks(x)
    ax.set_xticklabels(cats, rotation=45)
    ax.set_title("Budget vs Average Actual Spend (per month)")
    ax.set_ylabel(f"Amount ({RUPEE})")
    ax.legend()
    return _save(fig, "08_budget_vs_actual.png", save)


def anomaly_scatter(df, save=True):
    exp = an.expenses_only(df)
    anom = an.detect_anomalies(df)
    fig, ax = plt.subplots(figsize=(12, 5))
    ax.scatter(exp["Date"], exp["Amount"], s=10, alpha=0.4, color="gray", label="Normal")
    ax.scatter(anom["Date"], anom["Amount"], s=60, color="red", label="Anomaly (z > 3)")
    for _, r in anom.head(3).iterrows():
        ax.annotate(r["Description"], (r["Date"], r["Amount"]), fontsize=8,
                    xytext=(5, 5), textcoords="offset points")
    ax.set_yscale("log")
    ax.set_title("Transaction Amounts and Detected Anomalies (log scale)")
    ax.set_ylabel(f"Amount ({RUPEE})")
    ax.legend()
    return _save(fig, "09_anomalies.png", save)


def make_all(df, save=True):
    funcs = [category_bar, expense_pie, monthly_income_vs_expense, savings_rate_chart,
             weekday_chart, category_month_heatmap, payment_method_chart,
             budget_vs_actual, anomaly_scatter]
    figs = [f(df, save) for f in funcs]
    for fig in figs:
        plt.close(fig)
    return len(figs)