# Expense Tracker App - Complete Project Guide

## 1. Project explanation
**Simple:** an expense tracker records money coming in and going out, groups it into categories
(food, rent, travel) and shows where your money goes so you can spend smarter.
**Technical:** a pipeline that ingests transaction records (Date, Category, Description, Amount, Type,
Payment_Method), cleans and standardises them, aggregates by category/time, runs rule- and
statistics-based checks (budgets, z-score anomalies, trend forecast), and visualises results.

**Why it matters:** raw logs are overwhelming; summaries and charts turn them into decisions.
**Users:** individuals (budgeting, saving), small businesses (cost control, reimbursements), banks and
FinTech apps (spend insights, fraud flags). **Use cases:** personal finance tracking, business expense
monitoring, budgeting and cost control, financial planning.

**Workflow:** data input → storage (CSV) → cleaning → analysis → visualisation → insights → decisions.

## 2. Tech stack options
| Option | Tools | Dashboard | Difficulty |
|---|---|---|---|
| A (Easy) | Python, Pandas, Matplotlib, CSV, Jupyter | No | Easy |
| B (Intermediate) | A + Seaborn, Streamlit, modular `src/` code | Yes | Medium |
| C (Advanced) | B + SQL database (SQLite/Postgres), scikit-learn/Prophet forecasting, Plotly, FastAPI, Docker | Yes + API | Hard |

**Selected: Option B** - shows analysis, clean code structure and a demo-able app without the setup
burden of Option C. This repo is Option B with small taste of C (forecast, anomalies).

## 3. Architecture
```
 +-----------------+     +------------------+     +--------------------+
 | INPUT           | --> | PROCESSING       | --> | OUTPUT             |
 | synthetic CSV   |     | clean (src/      |     | outputs/*.csv      |
 | dashboard form  |     |  clean_data.py)  |     | images/*.png       |
 | (ESP32 buttons) |     | features         |     | insights_report.md |
 +-----------------+     | aggregate/trend  |     | Streamlit app      |
                         | budgets/anomaly  |     +--------------------+
                         +------------------+
 data/raw_expenses.csv -> data/cleaned_expenses.csv -> src/analysis.py -> visualize.py / insights.py -> app.py
```
Data flow: `generate_data.py` writes the raw CSV; `clean_data.py` produces the cleaned CSV with
Month/Weekday features; `analysis.py` computes tables; `visualize.py` and `insights.py` consume them;
`app.py` reads the same data and adds user-entered rows.

## 4. Implementation plan
| Phase | What to do | Why | Expected output | Mistake to avoid |
|---|---|---|---|---|
| 1 Setup | venv, install libs, create folders | reproducible environment | `pip list` shows libs | installing globally |
| 2 Data creation | run `generate_data.py` | no real data available | `raw_expenses.csv` (~750 rows) | forgetting a fixed seed |
| 3 Cleaning | run `clean_data.py` logic | trustworthy numbers | `cleaned_expenses.csv`, cleaning report | dropping rows silently - always report counts |
| 4 EDA | inspect shapes, distributions | understand before modelling | summary tables | skipping `.info()` / `.describe()` |
| 5 Feature engineering | Month, Weekday, Quarter, Is_Weekend | enables time analysis | new columns | sorting months as text names (use `2025-03`) |
| 6 Analysis | category, monthly, budget, anomaly, forecast | answer business questions | CSVs in `outputs/` | mixing income into expense totals |
| 7 Visualisation | 9 charts | communicate findings | PNGs in `images/` | no titles/units; too many colours |
| 8 Insights | plain-English findings | analysts must explain, not just plot | `insights_report.md` | stating numbers without a "so what" |
| 9 GitHub upload | commit in stages, push, add screenshots | proof of work | public repo | committing `venv/` |

## 5. Folder structure explained
- `data/` raw and cleaned CSVs. Keep raw untouched.
- `notebooks/` optional Jupyter exploration.
- `src/` reusable modules (config, data generation, cleaning, analysis, charts, insights).
- `outputs/` generated tables and the insights report.
- `images/` chart PNGs for README and proof.
- `hardware/` optional ESP32 sketch.
- `docs/` this guide.
- `README.md` first thing recruiters read. `requirements.txt` dependencies. `main.py` one-command pipeline. `app.py` dashboard.

## 6. Installation guide
**Ubuntu/Linux**
```bash
sudo apt update && sudo apt install python3 python3-venv python3-pip -y
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
```
**macOS**
```bash
brew install python
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
```
**Windows (PowerShell)**
```powershell
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```
Check: `python --version` (3.10+) and `python -c "import pandas; print(pandas.__version__)"`.
No local setup? Use Google Colab and `!pip install -r requirements.txt`.

## 7. Full project code
All code is in `src/`, `main.py` and `app.py`, commented and tested. Run order:
`generate_data.py` → `clean_data.py` → `analysis.py` → `visualize.py` → `insights.py` (all orchestrated by `main.py`),
then `app.py` for the dashboard.

## 8. Virtual simulation
1. **Fix the seed** (`SEED = 42`) so results are reproducible.
2. **Loop over every day of 2025.** On the 1st add salary; 5th rent; 10th/12th/15th bills; 20th/22nd subscriptions.
3. **Daily variable spending:** food most days (about 85%, 1.3x on weekends), transport on weekdays, entertainment on weekends, random health and shopping.
4. **Trends:** summer electricity x1.5 (Apr-Jun); shopping probability doubles in Oct-Nov (festive); travel more likely in May/Jun/Dec; education in Jan/Jun/Jul.
5. **Plant anomalies:** hospital visit (Mar 18, Rs 14,500), laptop repair (Aug 22, Rs 18,500), Diwali spree (Oct 20, Rs 12,000).
6. **Make it messy:** lowercase/UPPER/space-padded categories, "Rs 1,200" text amounts, missing values, bad dates, aliases ("Eating Out", "Cab"), duplicates.
7. **Clean → analyse.** Overspending = monthly category spend above `MONTHLY_BUDGETS`; anomaly = amount more than 3 standard deviations above its category mean.
8. **Final output:** summaries, 9 charts, insights report, dashboard.

**Proof to save:** terminal output of `python main.py`, all 9 PNGs, `insights_report.md`, dashboard screenshots.

## 9. How to run
```bash
python main.py --regen     # prints the 5 steps, writes data, outputs/, images/
streamlit run app.py       # http://localhost:8501
```
Expected: 752 raw rows → 731 clean rows, 9 charts, 8 insights, dashboard with KPIs, tabs for overview, budget alerts, anomalies, insights.

## 10. GitHub upload steps
1. On github.com click **New repository**. Name: `Expense-Tracker-App`. Public. No README (you already have one).
2. **Description:** "Data science expense tracker: synthetic data, cleaning, budget & anomaly detection, Streamlit dashboard (Python, Pandas, Seaborn)."
3. **Topics/tags:** `data-science` `python` `pandas` `streamlit` `data-visualization` `fintech` `expense-tracker` `personal-finance` `eda` `portfolio-project`
4. Terminal:
```bash
cd Expense-Tracker-App
git init
git add .
git commit -m "chore: project structure and requirements"
git branch -M main
git remote add origin https://github.com/arppitha-ai/Expense-Tracker-App.git
git push -u origin main
```
5. Good commit messages: `feat: add synthetic data generator`, `feat: add cleaning pipeline`, `feat: add category and monthly analysis`, `feat: add budget and anomaly detection`, `feat: add charts`, `feat: add Streamlit dashboard`, `docs: add README with screenshots`.
6. If prompted for a password, use a GitHub Personal Access Token (Settings → Developer settings), not your account password.

## 11. README
See the root `README.md` (ready to use).

## 12. Proof-building strategy (5 days)
| Day | Work | Commits | Proof screenshot |
|---|---|---|---|
| 1 Setup | venv, folders, requirements, README skeleton | `chore: project structure` | terminal showing `pip list` |
| 2 Dataset | `generate_data.py`, `clean_data.py` | `feat: synthetic data`, `feat: cleaning` | dataset preview, cleaning report |
| 3 Analysis | `analysis.py`, `insights.py` | `feat: analysis`, `feat: insights` | summary tables, insights report |
| 4 Visualisation | `visualize.py`, `app.py` | `feat: charts`, `feat: dashboard` | charts folder, dashboard |
| 5 Final upload | README polish, screenshots, tags, push | `docs: README with results` | GitHub repo page |

## 13. Screenshots to capture
1. Dataset preview (`head()` of the raw file showing messy rows) and cleaned preview
2. Cleaning report from terminal
3. Category-wise spending bar chart (`01`)
4. Pie chart (`02`)
5. Monthly trends (`03`) and savings rate (`04`)
6. Heatmap (`06`) and anomalies (`09`)
7. Dashboard: overview tab, budget alerts tab, insights tab
8. GitHub repo page with folders and tags
Save dashboard shots as `images/dashboard_overview.png` etc.

## 14. Interview preparation
**1. What is your project?** A data pipeline and dashboard that cleans transaction data, analyses spending, flags overspending and anomalies, and recommends actions.
**2. Why synthetic data?** Real financial data is private. I simulated realistic patterns with a fixed seed so results are reproducible, and the pipeline works unchanged on a real bank CSV with the same columns.
**3. How did you clean the data?** Removed duplicates, stripped and standardised category text, mapped aliases, converted "Rs 1,200" strings to numbers, coerced invalid dates, dropped untrustworthy rows and reported counts.
**4. How do you detect overspending?** Compare monthly category totals to budgets in `config.py`; every month above budget becomes an alert with the percentage overspend.
**5. How do you detect anomalies?** Per-category z-score; flag transactions more than 3 standard deviations above the category mean. Limitation: skewed data produces some false positives, so IQR or robust z-score are alternatives.
**6. What features did you engineer?** Month (as YYYY-MM), month name, quarter, weekday, weekend flag.
**7. What insights did you find?** Shopping was the biggest overspend driver (festive months), August and October missed the savings target, Saturdays have the highest daily spend.
**8. How does the forecast work?** Average of a 3-month moving average and a linear trend fit. It is a baseline; I would upgrade to Prophet/ARIMA with more history.
**9. Challenges?** Handling messy amounts and dates safely, keeping month ordering correct, and making synthetic data realistic.
**10. How would you scale it?** Move data to a SQL database, ingest bank/UPI statements, add user accounts, schedule the pipeline and deploy the dashboard.
**HR explanation:** "I built a tool that turns messy spending records into clear charts and advice, like a mini Google Pay insights feature, to practise the full analyst workflow."
**Technical explanation:** "Modular Python pipeline with Pandas for ETL, statistical checks for anomalies, Seaborn for charts, and Streamlit for an interactive layer, with reproducible synthetic data."

## 15. Future improvements
Mobile app (Flutter/React Native), real-time tracking via bank/UPI APIs or SMS parsing, AI spending prediction (Prophet, ARIMA, XGBoost), budget alerts (email/Telegram), savings-goal tracking, receipt OCR, multi-user login, SQL backend.

## 16. Troubleshooting
| Error | Cause | Fix |
|---|---|---|
| `ModuleNotFoundError: No module named 'pandas'` | venv not active or libs missing | `source venv/bin/activate` then `pip install -r requirements.txt` |
| `ModuleNotFoundError: No module named 'src'` | running from wrong folder | `cd Expense-Tracker-App` and run `python main.py` |
| `streamlit: command not found` | not installed in active venv | `pip install streamlit`, or `python -m streamlit run app.py` |
| `FileNotFoundError: cleaned_expenses.csv` | pipeline not run | `python main.py --regen` |
| Charts do not appear | headless backend (Agg) is used on purpose | open files in `images/`; dashboard shows charts in browser |
| `externally-managed-environment` on Ubuntu | pip outside a venv | create and activate a venv first |
| Rupee symbol shows as a box | font lacks glyph | install `fonts-dejavu` or write "Rs" |
| `git push` rejected / asks password | token needed or remote has commits | use a Personal Access Token; `git pull --rebase origin main` first |
| Port 8501 busy | another Streamlit app running | `streamlit run app.py --server.port 8502` |
| `venv/` got committed | missing `.gitignore` | `git rm -r --cached venv` then commit |
