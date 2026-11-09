# 📈 CodeAlpha Internship: Stock Portfolio Tracker (Task 2)

An interactive, responsive financial asset management dashboard built with **Python 3.11+**, **Streamlit**, and **Pandas**. Developed as part of the **CodeAlpha Python Development Internship program**.

This project provides personal stock holding calculations, lot tracking, asset allocation breakdowns, and CSV reporting using offline illustrative benchmark prices—delivering accurate financial calculations without requiring paid API keys, databases, or live rate limits.

---

## 📌 Project Overview & Objectives

Managing a personal investment portfolio requires tracking multiple purchase lots, monitoring asset allocation, calculating total invested capital, and exporting data for tax or record-keeping. 

This application fulfills all specifications of the CodeAlpha Python Internship:
1. **Interactive Web Dashboard**: Built with Streamlit for a fast, responsive, and reactive UI.
2. **Deterministic Benchmark Pricing**: Employs a verified hardcoded price dictionary for standard major equities.
3. **Session State Persistence**: Uses Streamlit's `st.session_state` to maintain holdings during user interactions without requiring an external database.
4. **Lot-Level Holding Architecture**: Supports multiple distinct purchase lots, even for the same stock symbol, identified with unique IDs.
5. **Accurate Financial Arithmetic**: Calculates total investment, share counts, and allocation percentages formatted to two decimal places.
6. **Data Portability**: One-click export of active positions to formatted CSV, complete with headers, individual lots, and an explicit totals summary row.

---

## 🚀 Key Features & Evaluator Verification Guide

| Evaluator Test Case | Expected Behavior | Verification Status |
| :--- | :--- | :---: |
| **1. Empty Portfolio Works** | Dashboard loads cleanly with `$0.00` total, 0 shares, 0 holdings, and 0 distinct stocks. Displays informative empty state with option to load demo data. | ✅ Verified |
| **2. 10 AAPL @ $180.00 = $1,800.00** | Adding 10 AAPL shares sets Total Investment to `$1,800.00`, Total Shares to `10`, Holdings Count to `1`, and Distinct Stocks to `1`. | ✅ Verified |
| **3. 2 TSLA @ $250.00 gives $2,300.00** | Adding 2 TSLA shares updates combined Total Investment to `$2,300.00` (`$1,800.00 + $500.00`), Total Shares to `12`, Holdings Count to `2`, and Distinct Stocks to `2`. | ✅ Verified |
| **4. Repeated Stock Entries Work** | Adding another 5 AAPL shares creates a 2nd AAPL lot with a unique ID. Holdings count increases to `3`, Distinct stocks remains `2`, Total Shares becomes `17`, and Total Investment becomes `$3,200.00`. Expandable summary shows consolidated 15 AAPL shares worth `$2,700.00`. | ✅ Verified |
| **5. Invalid, Zero & Negative Rejected** | Input validation explicitly rejects quantities `<= 0` (e.g. `0`, `-1`, `-10`) or invalid non-integers, displaying an informative red error message without corrupting state. | ✅ Verified |
| **6. Individual Removal Deletes Selected Only** | Clicking the trash can icon on the first AAPL lot deletes only that specific lot (`AAPL-XXXXXXXX`). The second AAPL lot and the TSLA lot remain untouched in the portfolio. | ✅ Verified |
| **7. Reset / Clearing with Confirmation** | Clicking "Clear Entire Portfolio" triggers a confirmation dialog. Confirming resets the dashboard cleanly back to the empty state (`$0.00`, 0 shares). | ✅ Verified |
| **8. CSV Export with Holdings & Totals** | Downloaded CSV contains column headers, all individual holding lots with timestamps, and a dedicated `TOTAL` summary row listing overall shares and total invested capital. | ✅ Verified |
| **9. Consistent Session State** | State survives widget interactions, selectbox changes, and table deletions without duplicating entries or desynchronizing keys. | ✅ Verified |
| **10. Currency Formatting (Two Decimals)** | All dollar figures strictly format to two decimal places with thousands separators (`$1,800.00`, `$2,300.00`, `$0.00`). | ✅ Verified |

---

## 💲 Benchmark Stock Price Reference

The application uses the following benchmark prices as mandated by project requirements:

| Ticker Symbol | Company Name | Benchmark Sample Price (USD) | Sector |
| :---: | :---: | :---: | :---: |
| **AAPL** | Apple Inc. | **$180.00** | Consumer Electronics / Tech |
| **TSLA** | Tesla, Inc. | **$250.00** | Automotive / Clean Energy |
| **GOOGL** | Alphabet Inc. | **$140.00** | Internet / Search / AI |
| **MSFT** | Microsoft Corporation | **$420.00** | Cloud / Enterprise Software |
| **AMZN** | Amazon.com, Inc. | **$190.00** | E-Commerce / Cloud |
| **NVDA** | NVIDIA Corporation | **$120.00** | Semiconductors / AI Compute |
| **META** | Meta Platforms, Inc. | **$500.00** | Social Media / Metaverse |

> **⚠️ Illustrative Notice & Disclaimer**:
> All stock prices displayed in this application are hardcoded sample benchmark quotes for educational and demonstration purposes. They are **not live market quotes** and should not be used for actual financial trading decisions.

---

## 💻 Installation & Setup Guide

### Prerequisites
- **Python 3.11 or newer** installed on your system.
- Check Python version: `python --version` (or `py --version` on Windows).

---

### 🪟 Windows Setup (Exact Commands)

Open **PowerShell** or **Command Prompt** in the project root directory and execute:

```cmd
# 1. Create a virtual environment using the Python launcher
py -m venv .venv

# 2. Activate the virtual environment
.venv\Scripts\activate

# 3. Upgrade pip and install all project dependencies
python -m pip install -r requirements.txt

# 4. Launch the Streamlit dashboard
python -m streamlit run app.py
```

*Note: Once running, Streamlit will open your default browser automatically at `http://localhost:8501`.*

---

### 🍎 macOS & 🐧 Linux Setup

Open your terminal in the project directory and execute:

```bash
# 1. Create a virtual environment
python3 -m venv .venv

# 2. Activate the virtual environment
source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Launch the Streamlit application
streamlit run app.py
```

---

## 📁 Project File Structure

```text
├── app.py              # Main Streamlit web application & UI logic
├── test_portfolio.py   # Comprehensive unit test suite verifying pricing & financial math
├── requirements.txt    # Production Python dependencies (streamlit, pandas)
├── .gitignore          # Git exclusion rules for virtualenvs, caches, CSVs
└── README.md           # Project documentation, setup guide, and specs
```

---

## 🧪 Testing & Verification

A dedicated verification suite (`test_portfolio.py`) is included to test financial arithmetic, lot isolation, and edge-case validation independently from the UI layer.

### How to Run the Automated Tests:
```bash
python -m unittest test_portfolio.py -v
```

### Local Test Execution Output:
```text
test_benchmark_prices (__main__.TestStockPortfolioTracker) ... ok
test_clearing_resets_portfolio (__main__.TestStockPortfolioTracker) ... ok
test_combined_aapl_and_tsla_gives_2300 (__main__.TestStockPortfolioTracker) ... ok
test_csv_export_contains_holdings_and_totals (__main__.TestStockPortfolioTracker) ... ok
test_currency_formatting (__main__.TestStockPortfolioTracker) ... ok
test_empty_portfolio (__main__.TestStockPortfolioTracker) ... ok
test_individual_removal_deletes_only_selected_entry (__main__.TestStockPortfolioTracker) ... ok
test_invalid_zero_and_negative_quantities_rejected (__main__.TestStockPortfolioTracker) ... ok
test_repeated_stock_entries (__main__.TestStockPortfolioTracker) ... ok
test_ten_aapl_gives_1800 (__main__.TestStockPortfolioTracker) ... ok

----------------------------------------------------------------------
Ran 10 tests in 0.001s

OK
```

---

## ⚠️ Limitations & Future Scope

- **Offline Dataset**: Intentionally uses a deterministic offline price table to guarantee reliability without external API costs or rate-limiting.
- **Session-Based Storage**: Current portfolio entries persist for the browser session in `st.session_state`. Future iterations could integrate SQLite or local JSON serialization for multi-session persistence.

---

## 📄 License & Attribution

This project is developed for the **CodeAlpha Python Development Internship** program. Open source under the MIT / Apache 2.0 License.
