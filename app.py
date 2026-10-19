"""Streamlit dashboard.   Run:  streamlit run app.py"""
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import streamlit as st

from src import analysis as an
from src import insights
from src.clean_data import clean_expenses
from src.config import CLEAN_FILE, MONTHLY_BUDGETS, RAW_FILE, USER_FILE
from src.generate_data import create_raw_dataset

st.set_page_config(page_title="Expense Tracker", page_icon="💰", layout="wide")
USER_COLS = ["Date", "Category", "Description", "Amount", "Type", "Payment_Method"]


@st.cache_data
def load_data(_version: float) -> pd.DataFrame:
    """Load the synthetic data (create it if missing) plus anything the user typed in."""
    raw = pd.read_csv(RAW_FILE) if RAW_FILE.exists() else create_raw_dataset()
    if USER_FILE.exists():
        raw = pd.concat([raw, pd.read_csv(USER_FILE)], ignore_index=True)
    df, _ = clean_expenses(raw)
    return df


def save_user_expense(row: dict):
    frame = pd.DataFrame([row], columns=USER_COLS)
    frame.to_csv(USER_FILE, mode="a", header=not USER_FILE.exists(), index=False)


# ------------------------------------------------------------------ sidebar
st.sidebar.header("➕ Add an expense")
with st.sidebar.form("add_form", clear_on_submit=True):
    d = st.date_input("Date")
    cat = st.selectbox("Category", list(MONTHLY_BUDGETS) + ["Salary", "Freelance", "Other"])
    desc = st.text_input("Description")
    amt = st.number_input("Amount (₹)", min_value=1.0, step=50.0)
    ttype = st.selectbox("Type", ["Expense", "Income"])
    pay = st.selectbox("Payment method", ["UPI", "Cash", "Credit Card", "Debit Card", "Bank Transfer"])
    if st.form_submit_button("Save"):
        save_user_expense({"Date": d, "Category": cat, "Description": desc,
                           "Amount": amt, "Type": ttype, "Payment_Method": pay})
        st.cache_data.clear()
        st.sidebar.success("Saved!")

version = USER_FILE.stat().st_mtime if USER_FILE.exists() else 0.0
df = load_data(version)

st.sidebar.header("🔍 Filters")
lo, hi = df["Date"].min().date(), df["Date"].max().date()
date_range = st.sidebar.date_input("Date range", (lo, hi), min_value=lo, max_value=hi)
cats = st.sidebar.multiselect("Categories", sorted(df["Category"].unique()),
                              default=sorted(df["Category"].unique()))
pays = st.sidebar.multiselect("Payment methods", sorted(df["Payment_Method"].unique()),
                              default=sorted(df["Payment_Method"].unique()))

f = df[df["Category"].isin(cats) & df["Payment_Method"].isin(pays)]
if isinstance(date_range, tuple) and len(date_range) == 2:
    f = f[(f["Date"].dt.date >= date_range[0]) & (f["Date"].dt.date <= date_range[1])]

# --------------------------------------------------------------------- main
st.title("💰 Expense Tracker Dashboard")
if f.empty:
    st.warning("No data for these filters.")
    st.stop()

k = an.kpis(f)
c1, c2, c3, c4 = st.columns(4)
c1.metric("Income", f"₹{k['total_income']:,.0f}")
c2.metric("Expense", f"₹{k['total_expense']:,.0f}")
c3.metric("Net savings", f"₹{k['net_savings']:,.0f}")
c4.metric("Savings rate", f"{k['savings_rate_pct']}%")

tab1, tab2, tab3, tab4 = st.tabs(["📊 Overview", "🚨 Budget alerts", "🔎 Anomalies", "🧠 Insights"])

with tab1:
    left, right = st.columns(2)
    cat_summary = an.category_summary(f)
    with left:
        st.subheader("Spending by category")
        st.bar_chart(cat_summary.set_index("Category")["Total"])
    with right:
        st.subheader("Expense distribution")
        pie = an.group_small_categories(cat_summary)
        fig, ax = plt.subplots()
        ax.pie(pie["Total"], autopct="%1.1f%%", startangle=90, pctdistance=0.78,
               wedgeprops=dict(width=0.45))
        ax.legend(pie["Category"], loc="center left", bbox_to_anchor=(1, 0.5), frameon=False)
        ax.axis("equal")
        st.pyplot(fig)
    st.subheader("Monthly income vs expense")
    st.line_chart(an.monthly_summary(f).set_index("Month")[["Income", "Expense"]])
    st.subheader("Month x category heatmap")
    fig, ax = plt.subplots(figsize=(11, 5))
    sns.heatmap(an.monthly_category_matrix(f), annot=True, fmt=".0f", cmap="YlOrRd", ax=ax)
    st.pyplot(fig)
    if st.checkbox("Show raw filtered data"):
        st.dataframe(f)

with tab2:
    st.subheader("Months where a category went over budget")
    alerts = an.budget_check(f)
    if alerts.empty:
        st.success("No budget overruns in this selection 🎉")
    else:
        st.dataframe(alerts, use_container_width=True)
        st.caption(f"{len(alerts)} overruns. Edit budgets in src/config.py")

with tab3:
    st.subheader("Unusually large transactions (z-score > 3)")
    st.dataframe(an.detect_anomalies(f), use_container_width=True)

with tab4:
    for i, line in enumerate(insights.generate_insights(f), 1):
        st.write(f"**{i}.** {line}")
    st.subheader("Recommendations")
    for line in insights.generate_recommendations(f):
        st.write(f"- {line}")