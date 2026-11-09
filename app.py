"""Stock Portfolio Tracker - CodeAlpha Internship Project.

A complete, responsive Python 3.11+ Streamlit dashboard for personal stock
portfolio tracking using hardcoded illustrative benchmark prices, input validation,
multi-lot tracking with unique IDs, accurate financial arithmetic, and CSV export.

Author: CodeAlpha Intern
Program: CodeAlpha Python Development Internship (Task 2)
"""

from __future__ import annotations

import csv
from datetime import datetime, timezone
import io
from typing import Any, Dict, List, Set, Tuple
import uuid

try:
    import streamlit as st
except ImportError:
    st = None  # Allows headless automated test runners to import pure business logic without streamlit installed


# ==============================================================================
# 1. HARDCODED BENCHMARK STOCK PRICES
# ==============================================================================
# Illustrative benchmark prices strictly matching project specification.
# Strictly disclosed in the UI as non-live reference values.
STOCK_PRICES: dict[str, float] = {
    "AAPL": 180.00,
    "TSLA": 250.00,
    "GOOGL": 140.00,
    "MSFT": 420.00,
    "AMZN": 190.00,
    "NVDA": 120.00,
    "META": 500.00,
}

STOCK_NAMES: dict[str, str] = {
    "AAPL": "Apple Inc.",
    "TSLA": "Tesla, Inc.",
    "GOOGL": "Alphabet Inc.",
    "MSFT": "Microsoft Corporation",
    "AMZN": "Amazon.com, Inc.",
    "NVDA": "NVIDIA Corporation",
    "META": "Meta Platforms, Inc.",
}

STOCK_SECTORS: dict[str, str] = {
    "AAPL": "Consumer Electronics / Tech",
    "TSLA": "Automotive / Clean Energy",
    "GOOGL": "Internet / Search / AI",
    "MSFT": "Cloud / Enterprise Software",
    "AMZN": "E-Commerce / Cloud Computing",
    "NVDA": "Semiconductors / AI Accelerators",
    "META": "Social Media / Digital Advertising",
}


# ==============================================================================
# 2. PURE BUSINESS & FINANCIAL LOGIC (Testable without Streamlit UI)
# ==============================================================================

def format_currency(amount: float) -> str:
    """Format floating point numbers as standardized USD currency string with two decimals.

    Examples:
        format_currency(0.0) -> "$0.00"
        format_currency(1800.0) -> "$1,800.00"
        format_currency(2300.0) -> "$2,300.00"
    """
    return f"${amount:,.2f}"


def calculate_holding_value(shares: int, price_per_share: float) -> float:
    """Calculate the total holding monetary value with 2-decimal rounding.

    Args:
        shares: Strictly positive integer representing quantity of shares.
        price_per_share: Unit price of the stock.

    Returns:
        float: Total value calculated as shares * price_per_share rounded to 2 decimals.

    Raises:
        ValueError: If shares is not a positive integer (> 0) or price_per_share is negative.
    """
    if not isinstance(shares, int) or isinstance(shares, bool) or shares <= 0:
        raise ValueError("Shares quantity must be a strictly positive integer greater than zero.")
    if price_per_share < 0:
        raise ValueError("Price per share cannot be negative.")
    return round(float(shares) * float(price_per_share), 2)


def create_holding_record(symbol: str, shares: int) -> dict[str, Any]:
    """Create a new portfolio holding record with a unique ID and UTC timestamp.

    Args:
        symbol: Stock ticker symbol (e.g., 'AAPL', 'TSLA').
        shares: Strictly positive integer number of shares.

    Returns:
        dict: Fully populated holding lot dictionary.

    Raises:
        KeyError: If symbol is not in the benchmark price catalog.
        ValueError: If shares is non-positive or not an integer.
    """
    clean_symbol = symbol.strip().upper()
    if clean_symbol not in STOCK_PRICES:
        raise KeyError(f"Ticker symbol '{symbol}' is not recognized in the benchmark price catalog.")

    if not isinstance(shares, int) or isinstance(shares, bool) or shares <= 0:
        raise ValueError("Quantity of shares must be a strictly positive integer greater than zero.")

    unit_price = STOCK_PRICES[clean_symbol]
    total_val = calculate_holding_value(shares, unit_price)
    unique_id = f"{clean_symbol}-{uuid.uuid4().hex[:8]}"
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

    return {
        "id": unique_id,
        "symbol": clean_symbol,
        "company_name": STOCK_NAMES.get(clean_symbol, clean_symbol),
        "sector": STOCK_SECTORS.get(clean_symbol, "General Equities"),
        "shares": int(shares),
        "price_per_share": unit_price,
        "total_value": total_val,
        "added_at": timestamp,
    }


def calculate_portfolio_summary(holdings: list[dict[str, Any]]) -> dict[str, Any]:
    """Calculate aggregate summary metrics across all active portfolio lots.

    Handles empty portfolio state, repeated symbols, and consolidated asset breakdown.

    Args:
        holdings: List of active holding records.

    Returns:
        dict containing:
            - total_investment: float (2-decimal rounded sum)
            - total_shares: int (sum of shares)
            - holdings_count: int (total number of lots)
            - distinct_stocks: int (count of unique ticker symbols)
            - symbol_breakdown: dict of consolidated data per symbol
    """
    if not holdings:
        return {
            "total_investment": 0.00,
            "total_shares": 0,
            "holdings_count": 0,
            "distinct_stocks": 0,
            "symbol_breakdown": {},
        }

    total_investment = round(sum(h["total_value"] for h in holdings), 2)
    total_shares = sum(h["shares"] for h in holdings)
    holdings_count = len(holdings)
    distinct_stocks = len(set(h["symbol"] for h in holdings))

    # Aggregate repeat purchases by ticker symbol
    breakdown: dict[str, dict[str, Any]] = {}
    for h in holdings:
        sym = h["symbol"]
        if sym not in breakdown:
            breakdown[sym] = {
                "shares": 0,
                "total_value": 0.00,
                "price_per_share": h["price_per_share"],
                "company_name": h["company_name"],
                "sector": h.get("sector", ""),
                "lots_count": 0,
            }
        breakdown[sym]["shares"] += h["shares"]
        breakdown[sym]["total_value"] = round(breakdown[sym]["total_value"] + h["total_value"], 2)
        breakdown[sym]["lots_count"] += 1

    return {
        "total_investment": total_investment,
        "total_shares": total_shares,
        "holdings_count": holdings_count,
        "distinct_stocks": distinct_stocks,
        "symbol_breakdown": breakdown,
    }


def export_portfolio_to_csv(holdings: list[dict[str, Any]]) -> str:
    """Generate a clean, standardized CSV string containing all holdings and summary totals.

    Args:
        holdings: List of active holding records.

    Returns:
        str: CSV content with headers, individual lot rows, and an explicit totals summary row.
    """
    output = io.StringIO()
    writer = csv.writer(output, lineterminator="\n")

    # Header row
    writer.writerow([
        "Holding ID",
        "Stock Symbol",
        "Company Name",
        "Shares",
        "Sample Price Per Share (USD)",
        "Total Investment Value (USD)",
        "Date Added (UTC)",
    ])

    if not holdings:
        writer.writerow([
            "NO_HOLDINGS",
            "N/A",
            "Portfolio is currently empty",
            0,
            "0.00",
            "0.00",
            datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
        ])
        writer.writerow([])
        writer.writerow([
            "TOTAL",
            "0 Distinct Stocks",
            "0 Total Holdings",
            0,
            "N/A",
            "0.00",
            datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
        ])
        return output.getvalue()

    total_investment = 0.0
    total_shares = 0
    distinct_symbols: set[str] = set()

    for h in holdings:
        total_investment += h["total_value"]
        total_shares += h["shares"]
        distinct_symbols.add(h["symbol"])
        writer.writerow([
            h["id"],
            h["symbol"],
            h["company_name"],
            h["shares"],
            f"{h['price_per_share']:.2f}",
            f"{h['total_value']:.2f}",
            h["added_at"],
        ])

    # Append an explicit Totals Summary row
    writer.writerow([])
    writer.writerow([
        "TOTAL",
        f"{len(distinct_symbols)} Distinct Stocks",
        f"{len(holdings)} Total Holdings",
        total_shares,
        "N/A",
        f"{total_investment:.2f}",
        datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
    ])

    return output.getvalue()


# ==============================================================================
# 3. STREAMLIT SESSION STATE MANAGEMENT
# ==============================================================================

def init_session_state() -> None:
    """Initialize Streamlit session state stores with consistent keys.

    Starts with an empty portfolio by default so all initial test cases (empty portfolio,
    adding 10 AAPL to reach 1800.00, adding 2 TSLA to reach 2300.00) work cleanly.
    """
    if "holdings" not in st.session_state:
        st.session_state.holdings = []

    if "show_clear_confirm" not in st.session_state:
        st.session_state.show_clear_confirm = False


def add_holding_action(symbol: str, shares: int) -> bool:
    """Validate and add a holding to the session state."""
    try:
        new_holding = create_holding_record(symbol, shares)
        st.session_state.holdings.append(new_holding)
        return True
    except (ValueError, KeyError) as err:
        st.error(f"❌ Could not add holding: {err}")
        return False


def remove_holding_action(holding_id: str) -> bool:
    """Remove a specific holding matching unique holding_id."""
    initial_count = len(st.session_state.holdings)
    st.session_state.holdings = [
        h for h in st.session_state.holdings if h["id"] != holding_id
    ]
    return len(st.session_state.holdings) < initial_count


def clear_portfolio_action() -> None:
    """Clear all holdings from the active session and reset confirmation flag."""
    st.session_state.holdings = []
    st.session_state.show_clear_confirm = False


def load_demo_portfolio() -> None:
    """Utility to populate sample holdings for quick demonstration."""
    demo_entries = [
        ("AAPL", 10),
        ("TSLA", 2),
        ("NVDA", 15),
    ]
    st.session_state.holdings = [
        create_holding_record(sym, qty) for sym, qty in demo_entries
    ]


# ==============================================================================
# 4. STREAMLIT USER INTERFACE COMPONENTS
# ==============================================================================

def render_header() -> None:
    """Render top application title, metadata badge, and illustrative quote disclaimer."""
    col1, col2 = st.columns([3, 1])
    with col1:
        st.title("📈 Stock Portfolio Tracker")
        st.caption("CodeAlpha Python Development Internship • Task 2 Dashboard")
    with col2:
        st.markdown(
            """
            <div style="text-align: right; padding-top: 10px;">
                <span style="background: linear-gradient(135deg, #10b981, #059669); color: white; padding: 5px 12px; border-radius: 9999px; font-size: 0.8rem; font-weight: 700; letter-spacing: 0.05em; text-transform: uppercase;">
                    CodeAlpha Python
                </span>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # Mandatory illustrative benchmark price disclosure
    st.warning(
        "⚠️ **Illustrative Benchmark Quotes Notice**: All stock prices across this application "
        "(AAPL: $180.00, TSLA: $250.00, GOOGL: $140.00, MSFT: $420.00, AMZN: $190.00, NVDA: $120.00, META: $500.00) "
        "are pre-configured illustrative figures for academic simulation and evaluation. "
        "These are **not** live market quotes.",
        icon="ℹ️",
    )


def render_summary_cards(summary: dict[str, Any]) -> None:
    """Render the 4 primary KPI summary metric cards."""
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            label="Total Investment",
            value=format_currency(summary["total_investment"]),
            help="Cumulative dollar value of all active holdings, formatted with two decimals.",
        )
    with col2:
        st.metric(
            label="Total Shares",
            value=f"{summary['total_shares']:,}",
            help="Total aggregate quantity of shares across all active lots.",
        )
    with col3:
        st.metric(
            label="Holdings Count",
            value=f"{summary['holdings_count']} {'lot' if summary['holdings_count'] == 1 else 'lots'}",
            help="Total individual lot transactions (supports multiple purchases of the same stock).",
        )
    with col4:
        st.metric(
            label="Distinct Stocks",
            value=f"{summary['distinct_stocks']} {'ticker' if summary['distinct_stocks'] == 1 else 'tickers'}",
            help="Total count of unique company ticker symbols present in the portfolio.",
        )


def render_add_holding_form() -> None:
    """Render the sidebar form for adding new holdings with live price feedback."""
    st.sidebar.header("➕ Add Stock Holding")
    st.sidebar.caption("Select a stock ticker and specify a positive quantity of shares.")

    symbols = list(STOCK_PRICES.keys())

    def format_dropdown_option(sym: str) -> str:
        return f"{sym} • {STOCK_NAMES.get(sym, sym)} ({format_currency(STOCK_PRICES[sym])})"

    selected_symbol = st.sidebar.selectbox(
        "Choose Stock Symbol",
        options=symbols,
        format_func=format_dropdown_option,
        index=0,
        key="selected_symbol_dropdown",
        help="Select any of the supported benchmark stocks.",
    )

    sample_price = STOCK_PRICES[selected_symbol]
    company_name = STOCK_NAMES[selected_symbol]
    sector = STOCK_SECTORS.get(selected_symbol, "")

    # Live automatic sample-price feedback container
    st.sidebar.info(
        f"**Sample Price**: `{format_currency(sample_price)}`  \n"
        f"**Company**: {company_name}  \n"
        f"**Sector**: {sector}",
        icon="🏷️",
    )

    # Quantity input (step=1 allows user to enter positive integers, and test 0 or negative values)
    shares_input = st.sidebar.number_input(
        "Quantity of Shares (Positive Integer)",
        value=10,
        step=1,
        key="shares_quantity_input",
        help="Enter the number of shares to purchase. Must be a strictly positive integer (> 0).",
    )

    # Dynamic pre-calculation feedback
    if shares_input > 0:
        estimated_cost = calculate_holding_value(int(shares_input), sample_price)
        st.sidebar.markdown(
            f"**Estimated Lot Value**: `{format_currency(estimated_cost)}`  \n"
            f"*(Calculated as {int(shares_input)} shares × {format_currency(sample_price)})*"
        )
    else:
        st.sidebar.caption("⚠️ Enter a quantity greater than zero to calculate lot value.")

    # Form submission button
    if st.sidebar.button("Add to Portfolio", type="primary", use_container_width=True, key="btn_add_holding"):
        if shares_input is None or shares_input <= 0:
            st.sidebar.error("❌ Invalid quantity: Number of shares must be a strictly positive integer greater than zero.")
        else:
            success = add_holding_action(selected_symbol, int(shares_input))
            if success:
                st.sidebar.success(
                    f"✅ Added {int(shares_input)} shares of {selected_symbol} ({format_currency(int(shares_input) * sample_price)})!"
                )
                st.rerun()

    st.sidebar.divider()

    # Benchmark Price Reference Table
    st.sidebar.subheader("📋 Benchmark Price Reference")
    ref_data = [
        {"Ticker": sym, "Company": STOCK_NAMES[sym], "Sample Price": format_currency(price)}
        for sym, price in STOCK_PRICES.items()
    ]
    st.sidebar.dataframe(ref_data, hide_index=True, use_container_width=True)


def render_holdings_view(holdings: list[dict[str, Any]], summary: dict[str, Any]) -> None:
    """Render the active holdings table, lot removal, and CSV export controls."""
    st.subheader("📋 Active Portfolio Holdings")

    # Empty State Handling
    if not holdings:
        st.info(
            "ℹ️ **Your portfolio is currently empty.**  \n"
            "Use the **Add Stock Holding** form in the sidebar to add your first position, "
            "or click the button below to load a sample demo portfolio.",
            icon="📭",
        )
        col_load, _ = st.columns([1, 2])
        with col_load:
            if st.button("🔄 Load Demo Portfolio (AAPL, TSLA, NVDA)", type="secondary", key="btn_load_demo"):
                load_demo_portfolio()
                st.rerun()
        return

    # Expandable Consolidated Summary (Groups multiple lots of the same ticker)
    if summary["holdings_count"] > 1:
        with st.expander("📊 Consolidated Asset Allocation (Grouped by Ticker)", expanded=False):
            breakdown = summary["symbol_breakdown"]
            breakdown_rows = []
            for sym, data in breakdown.items():
                pct = (data["total_value"] / summary["total_investment"] * 100) if summary["total_investment"] > 0 else 0
                breakdown_rows.append({
                    "Ticker": sym,
                    "Company": data["company_name"],
                    "Total Shares": data["shares"],
                    "Benchmark Price": format_currency(data["price_per_share"]),
                    "Consolidated Value": format_currency(data["total_value"]),
                    "Portfolio Weight": f"{pct:.1f}%",
                    "Lots Count": data["lots_count"],
                })
            st.dataframe(breakdown_rows, hide_index=True, use_container_width=True)

    # Detailed Holdings Table with Individual Lot Controls
    st.caption(f"Displaying **{len(holdings)}** individual holding {'lot' if len(holdings) == 1 else 'lots'}:")

    # Table Header
    h1, h2, h3, h4, h5, h6 = st.columns([1.5, 2.5, 1.2, 1.8, 2.0, 1.2])
    with h1:
        st.markdown("**Ticker / Lot ID**")
    with h2:
        st.markdown("**Company Name**")
    with h3:
        st.markdown("**Shares**")
    with h4:
        st.markdown("**Price / Share**")
    with h5:
        st.markdown("**Total Value**")
    with h6:
        st.markdown("**Action**")

    # Table Rows
    for item in holdings:
        c1, c2, c3, c4, c5, c6 = st.columns([1.5, 2.5, 1.2, 1.8, 2.0, 1.2])
        with c1:
            st.markdown(f"**{item['symbol']}**")
            st.caption(item["id"])
        with c2:
            st.text(item["company_name"])
        with c3:
            st.markdown(f"`{item['shares']:,}`")
        with c4:
            st.text(format_currency(item["price_per_share"]))
        with c5:
            st.markdown(f"**{format_currency(item['total_value'])}**")
        with c6:
            if st.button("🗑️", key=f"del_btn_{item['id']}", help=f"Remove lot {item['id']}"):
                remove_holding_action(item["id"])
                st.rerun()

    st.divider()

    # Bottom Actions: CSV Download & Clear Portfolio
    col_dl, col_clr = st.columns([1, 1], gap="medium")

    with col_dl:
        csv_payload = export_portfolio_to_csv(holdings)
        file_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        st.download_button(
            label="📥 Download Portfolio CSV",
            data=csv_payload,
            file_name=f"stock_portfolio_{file_timestamp}.csv",
            mime="text/csv",
            use_container_width=True,
            key="btn_download_csv",
            help="Download all current holdings and totals as a formatted CSV file.",
        )

    with col_clr:
        if not st.session_state.show_clear_confirm:
            if st.button("🧹 Clear Entire Portfolio", type="secondary", use_container_width=True, key="btn_trigger_clear"):
                st.session_state.show_clear_confirm = True
                st.rerun()
        else:
            st.warning("⚠️ **Confirm Reset**: Delete all holdings from this session?")
            conf_yes, conf_no = st.columns(2)
            with conf_yes:
                if st.button("🚨 Yes, Clear All", type="primary", use_container_width=True, key="btn_confirm_clear_yes"):
                    clear_portfolio_action()
                    st.rerun()
            with conf_no:
                if st.button("Cancel", use_container_width=True, key="btn_confirm_clear_cancel"):
                    st.session_state.show_clear_confirm = False
                    st.rerun()


# ==============================================================================
# 5. MAIN APPLICATION ENTRYPOINT
# ==============================================================================

def main() -> None:
    """Main execution routine for the Streamlit dashboard."""
    if st is None:
        print("Streamlit is required to launch the interactive UI. Run via: python -m streamlit run app.py")
        return

    st.set_page_config(
        page_title="Stock Portfolio Tracker | CodeAlpha",
        page_icon="📈",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    init_session_state()
    render_header()

    # Calculate reactive summaries
    summary = calculate_portfolio_summary(st.session_state.holdings)
    render_summary_cards(summary)

    st.write("")  # Spacing

    # Render sidebar form
    render_add_holding_form()

    # Render main holdings view
    render_holdings_view(st.session_state.holdings, summary)

    # Footer
    st.divider()
    st.markdown(
        """
        <div style="text-align: center; color: #64748b; font-size: 0.8rem; padding: 8px 0;">
            CodeAlpha Internship Project: <strong>Stock Portfolio Tracker</strong> (Task 2) | Python 3.11+ &amp; Streamlit<br>
            All price calculations utilize illustrative benchmark quotes. No live trading or external broker connectivity.
        </div>
        """,
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
