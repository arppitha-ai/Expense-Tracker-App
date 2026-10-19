"""Central configuration: paths, budgets and thresholds.
Change values here instead of hunting through the code."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
OUTPUT_DIR = ROOT / "outputs"
IMAGE_DIR = ROOT / "images"

RAW_FILE = DATA_DIR / "raw_expenses.csv"          # messy synthetic data
CLEAN_FILE = DATA_DIR / "cleaned_expenses.csv"    # output of cleaning step
USER_FILE = DATA_DIR / "user_expenses.csv"        # expenses typed in the dashboard

YEAR = 2025
SEED = 42  # fixed seed -> everyone gets identical data (reproducible)

# Monthly budget per category (Rs). Used for overspending detection.
MONTHLY_BUDGETS = {
    "Rent": 12000,
    "Food": 7000,
    "Transport": 2500,
    "Bills": 3000,
    "Shopping": 4000,
    "Entertainment": 2000,
    "Health": 1500,
    "Travel": 3000,
    "Education": 1500,
    "Subscriptions": 900,
}

ANOMALY_Z_THRESHOLD = 3.0   # a transaction >3 std-devs above its category mean is flagged
TARGET_SAVINGS_RATE = 20.0  # % of income we want to save
