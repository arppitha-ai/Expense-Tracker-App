"""Step 5 - Turn numbers into plain-English insights and recommendations."""
from . import analysis as an
from .config import OUTPUT_DIR, TARGET_SAVINGS_RATE

R = "Rs "


def generate_insights(df) -> list:
    k = an.kpis(df)
    cat = an.category_summary(df)
    mon = an.monthly_summary(df)
    wk = an.weekday_pattern(df)
    alerts = an.budget_check(df)
    anom = an.detect_anomalies(df)
    fc = an.forecast_next_month(mon)
    ins = []

    ins.append(f"Total income {R}{k['total_income']:,.0f}, total expense {R}{k['total_expense']:,.0f}; "
               f"net savings {R}{k['net_savings']:,.0f} ({k['savings_rate_pct']}% savings rate).")

    top = cat.iloc[0]
    flexible = cat[cat["Category"] != "Rent"].iloc[0]
    ins.append(f"{top['Category']} is the largest category ({top['Share_%']}% of spending). "
               f"Excluding fixed rent, {flexible['Category']} leads with {R}{flexible['Total']:,.0f}.")

    hi, lo = mon.loc[mon["Expense"].idxmax()], mon.loc[mon["Expense"].idxmin()]
    ins.append(f"Highest-spend month: {hi['Month']} ({R}{hi['Expense']:,.0f}); "
               f"lowest: {lo['Month']} ({R}{lo['Expense']:,.0f}).")

    below = mon[mon["Savings_Rate_%"] < TARGET_SAVINGS_RATE]
    if len(below):
        names = ", ".join(below["Month"])
        ins.append(f"{len(below)} month(s) missed the {TARGET_SAVINGS_RATE:.0f}% savings target: {names}.")
    else:
        ins.append(f"Every month met the {TARGET_SAVINGS_RATE:.0f}% savings target.")

    best, worst = wk.loc[wk["Avg_Daily_Spend"].idxmax()], wk.loc[wk["Avg_Daily_Spend"].idxmin()]
    ins.append(f"{best['Weekday']} has the highest average daily spend ({R}{best['Avg_Daily_Spend']:,.0f}); "
               f"{worst['Weekday']} the lowest ({R}{worst['Avg_Daily_Spend']:,.0f}).")

    if len(alerts):
        by_cat = alerts.groupby("Category")["Overspend"].agg(["count", "sum"]).sort_values("sum", ascending=False)
        c = by_cat.index[0]
        ins.append(f"Budgets were exceeded {len(alerts)} times across categories. Worst offender: {c} "
                   f"({int(by_cat.loc[c, 'count'])} months over, {R}{by_cat.loc[c, 'sum']:,.0f} total overspend).")
    else:
        ins.append("No category exceeded its monthly budget.")

    if len(anom):
        a = anom.iloc[0]
        ins.append(f"{len(anom)} unusually large transactions detected. Biggest: '{a['Description']}' "
                   f"({R}{a['Amount']:,.0f} on {a['Date']:%Y-%m-%d}).")

    ins.append(f"Baseline forecast for next month's expenses: about {R}{fc['blended']:,.0f} "
               f"(3-month average {R}{fc['moving_avg_3m']:,.0f}, linear trend {R}{fc['linear_trend']:,.0f}).")
    return ins


def generate_recommendations(df) -> list:
    cat = an.category_summary(df).set_index("Category")
    alerts = an.budget_check(df)
    recs = []
    if "Shopping" in cat.index and cat.loc["Shopping", "Share_%"] > 12:
        recs.append("Set a festive-season shopping cap and use a 48-hour wait rule for purchases above Rs 2,000.")
    if len(alerts) and (alerts["Category"] == "Food").sum() >= 3:
        recs.append("Food budget is breached often: plan weekly groceries and cut delivery orders.")
    if "Uncategorized" in cat.index:
        recs.append("Some transactions have no category; require a category at entry for cleaner reports.")
    recs.append("Create an emergency fund so one-off costs (medical, repairs) do not wipe out a month's savings.")
    recs.append("Review recurring subscriptions every quarter and cancel unused ones.")
    return recs


def write_report(df, path=None):
    path = path or OUTPUT_DIR / "insights_report.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = ["# Expense Insights Report", "", "## Key insights", ""]
    lines += [f"{i}. {t}" for i, t in enumerate(generate_insights(df), 1)]
    lines += ["", "## Recommendations", ""]
    lines += [f"- {t}" for t in generate_recommendations(df)]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path
