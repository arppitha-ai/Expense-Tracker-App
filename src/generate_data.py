"""Step 1 - Create SYNTHETIC expense data (no real bank data needed).

The data mimics one person's year: monthly salary, rent, bills, daily food,
weekday commuting, weekend entertainment, festive-season shopping (Oct/Nov),
a few one-off big expenses (anomalies) and some deliberately MESSY rows so the
cleaning step has real work to do.
"""
import numpy as np
import pandas as pd

from .config import RAW_FILE, SEED, YEAR

# payment methods and their probabilities, per category
PAYMENT = {
    "Food": (["UPI", "Cash", "Credit Card", "Debit Card"], [0.55, 0.20, 0.15, 0.10]),
    "Transport": (["UPI", "Cash", "Debit Card"], [0.60, 0.30, 0.10]),
    "Shopping": (["Credit Card", "UPI", "Debit Card"], [0.50, 0.35, 0.15]),
    "Entertainment": (["UPI", "Credit Card", "Cash"], [0.50, 0.35, 0.15]),
    "Health": (["UPI", "Debit Card", "Cash"], [0.40, 0.30, 0.30]),
    "Travel": (["Credit Card", "UPI", "Debit Card"], [0.55, 0.30, 0.15]),
    "Education": (["UPI", "Credit Card"], [0.60, 0.40]),
    "Subscriptions": (["Credit Card", "UPI"], [0.70, 0.30]),
    "Bills": (["UPI", "Bank Transfer"], [0.70, 0.30]),
    "Rent": (["Bank Transfer"], [1.0]),
    "Salary": (["Bank Transfer"], [1.0]),
    "Freelance": (["Bank Transfer", "UPI"], [0.5, 0.5]),
}

FOOD_ITEMS = ["Breakfast", "Lunch", "Dinner", "Zomato order", "Swiggy order",
              "Groceries", "Snacks", "Cafe", "Pizza order"]
TRANSPORT_ITEMS = ["Uber ride", "Metro card recharge", "Auto fare", "Fuel", "Bus pass"]
SHOP_ITEMS = ["Clothes", "Amazon order", "Flipkart order", "Shoes", "Gadget accessory", "Home items"]
ENT_ITEMS = ["Movie tickets", "Concert", "Gaming", "Dinner out with friends", "Bowling"]
HEALTH_ITEMS = ["Pharmacy", "Doctor consultation", "Lab tests", "Gym fee"]
TRAVEL_ITEMS = ["Train tickets", "Flight tickets", "Hotel stay", "Weekend trip"]
EDU_ITEMS = ["Online course", "Books", "Certification exam fee"]


def generate_expenses(year: int = YEAR, seed: int = SEED) -> pd.DataFrame:
    """Return a CLEAN synthetic transaction table for one year."""
    rng = np.random.default_rng(seed)
    rows = []

    def add(date, category, desc, amount, ttype):
        methods, probs = PAYMENT[category]
        rows.append({
            "Date": date.strftime("%Y-%m-%d"),
            "Category": category,
            "Description": str(desc),
            "Amount": int(round(amount)),
            "Type": ttype,
            "Payment_Method": str(rng.choice(methods, p=probs)),
        })

    for day in pd.date_range(f"{year}-01-01", f"{year}-12-31"):
        m, d = day.month, day.day
        weekend = day.dayofweek >= 5

        # ---- Income -------------------------------------------------------
        if d == 1:
            add(day, "Salary", "Monthly salary", 50000, "Income")
        if d == 25 and rng.random() < 0.4:
            add(day, "Freelance", "Freelance project payment",
                round(rng.uniform(3000, 9000), -2), "Income")

        # ---- Fixed monthly costs -----------------------------------------
        if d == 5:
            add(day, "Rent", "House rent", 12000, "Expense")
        if d == 10:
            summer = 1.5 if m in (4, 5, 6) else 1.0   # AC usage -> higher bill
            add(day, "Bills", "Electricity bill", rng.uniform(900, 1500) * summer, "Expense")
        if d == 12:
            add(day, "Bills", "Internet bill", 799, "Expense")
        if d == 15:
            add(day, "Bills", "Mobile recharge", 399, "Expense")
        if d == 20:
            add(day, "Subscriptions", "Netflix", 649, "Expense")
        if d == 22:
            add(day, "Subscriptions", "Spotify", 119, "Expense")
        if d == 8 and m in (1, 6, 7):
            add(day, "Education", rng.choice(EDU_ITEMS), rng.uniform(1500, 4500), "Expense")

        # ---- Variable daily spending -------------------------------------
        if rng.random() < 0.85:                                   # food
            n = 1 + int(rng.random() < (0.45 if weekend else 0.20))
            for _ in range(n):
                amt = rng.lognormal(np.log(170), 0.45) * (1.3 if weekend else 1.0)
                add(day, "Food", rng.choice(FOOD_ITEMS), amt, "Expense")

        if not weekend and rng.random() < 0.65:                   # commute
            add(day, "Transport", rng.choice(TRANSPORT_ITEMS),
                rng.lognormal(np.log(120), 0.6), "Expense")

        shop_p = 0.25 if m in (10, 11) else (0.18 if m == 12 else 0.12)   # festive season
        if rng.random() < shop_p:
            add(day, "Shopping", rng.choice(SHOP_ITEMS), rng.lognormal(np.log(900), 0.6), "Expense")

        if weekend and rng.random() < 0.35:                       # weekend fun
            add(day, "Entertainment", rng.choice(ENT_ITEMS), rng.lognormal(np.log(500), 0.4), "Expense")

        if rng.random() < 0.04:                                   # health
            add(day, "Health", rng.choice(HEALTH_ITEMS), rng.lognormal(np.log(600), 0.7), "Expense")

        travel_p = 0.035 if m in (5, 6, 12) else 0.01             # holiday seasons
        if rng.random() < travel_p:
            add(day, "Travel", rng.choice(TRAVEL_ITEMS), rng.uniform(2000, 6000), "Expense")

        # ---- One-off big expenses (these become our "anomalies") ----------
        if (m, d) == (3, 18):
            add(day, "Health", "Emergency hospital visit", 14500, "Expense")
        if (m, d) == (8, 22):
            add(day, "Shopping", "Laptop repair + accessories", 18500, "Expense")
        if (m, d) == (10, 20):
            add(day, "Shopping", "Diwali shopping spree", 12000, "Expense")

    return pd.DataFrame(rows)


def make_messy(df: pd.DataFrame, seed: int = SEED) -> pd.DataFrame:
    """Inject realistic data-quality problems so cleaning is meaningful."""
    rng = np.random.default_rng(seed + 1)
    df = df.copy().astype(object)
    n = len(df)

    # keep the three planted one-off expenses intact so the anomaly demo always works
    protected = df["Description"].isin(
        ["Emergency hospital visit", "Laptop repair + accessories", "Diwali shopping spree"])
    candidates = df.index[~protected]

    def pick(frac):
        return candidates[rng.choice(len(candidates), int(n * frac), replace=False)]

    i = pick(0.04); df.loc[i, "Category"] = df.loc[i, "Category"].str.lower()      # food
    i = pick(0.03); df.loc[i, "Category"] = df.loc[i, "Category"].str.upper()      # FOOD
    i = pick(0.03); df.loc[i, "Category"] = "  " + df.loc[i, "Category"] + " "     # spaces
    i = pick(0.02); df.loc[i, "Amount"] = df.loc[i, "Amount"].apply(lambda v: f"Rs {int(v):,}")  # text
    i = pick(0.015); df.loc[i, "Amount"] = np.nan                                  # missing amount
    i = pick(0.01); df.loc[i, "Category"] = np.nan                                 # missing category
    i = pick(0.005); df.loc[i, "Date"] = "N/A"                                     # bad date

    cat = df["Category"].astype(str).str.strip().str.lower()
    food = df.index[cat == "food"]
    df.loc[rng.choice(food, 25, replace=False), "Category"] = "Eating Out"         # alias
    transport = df.index[cat == "transport"]
    df.loc[rng.choice(transport, 15, replace=False), "Category"] = "Cab"          # alias

    dupes = df.sample(frac=0.01, random_state=seed)                                # duplicates
    df = pd.concat([df, dupes]).sort_values("Date", kind="mergesort").reset_index(drop=True)
    return df


def create_raw_dataset(path=RAW_FILE) -> pd.DataFrame:
    path.parent.mkdir(parents=True, exist_ok=True)
    messy = make_messy(generate_expenses())
    messy.to_csv(path, index=False)
    return messy


if __name__ == "__main__":
    out = create_raw_dataset()
    print(f"Created {RAW_FILE} with {len(out)} rows")
