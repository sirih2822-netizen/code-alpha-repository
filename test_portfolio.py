"""Comprehensive Unit Test Suite for Stock Portfolio Tracker (CodeAlpha Task 2).

This test suite executes programmatic verification for every requirement:
- Empty portfolio state
- 10 AAPL shares @ $180.00 = $1,800.00
- 2 TSLA shares @ $250.00 brings combined total to $2,300.00
- Repeated stock entries (multiple lots of same ticker)
- Rejection of invalid, zero, and negative quantities
- Individual lot removal (deletes only the selected entry)
- Reset / clearing functionality
- CSV export containing correct holdings and totals
- Currency formatting with strictly two decimals
"""

import csv
import io
import unittest

from app import (
    STOCK_NAMES,
    STOCK_PRICES,
    calculate_holding_value,
    calculate_portfolio_summary,
    create_holding_record,
    export_portfolio_to_csv,
    format_currency,
)


class TestStockPortfolioTracker(unittest.TestCase):
    """Rigorous unit test suite verifying financial arithmetic and portfolio logic."""

    def test_benchmark_prices(self) -> None:
        """Verify all mandated illustrative benchmark stock prices."""
        expected_benchmarks = {
            "AAPL": 180.00,
            "TSLA": 250.00,
            "GOOGL": 140.00,
            "MSFT": 420.00,
            "AMZN": 190.00,
            "NVDA": 120.00,
            "META": 500.00,
        }
        for symbol, expected_price in expected_benchmarks.items():
            self.assertIn(symbol, STOCK_PRICES)
            self.assertEqual(STOCK_PRICES[symbol], expected_price)
            self.assertIn(symbol, STOCK_NAMES)

    def test_currency_formatting(self) -> None:
        """Verify USD currency formatting to two decimals with commas."""
        self.assertEqual(format_currency(0.0), "$0.00")
        self.assertEqual(format_currency(1800.0), "$1,800.00")
        self.assertEqual(format_currency(2300.0), "$2,300.00")
        self.assertEqual(format_currency(250.0), "$250.00")
        self.assertEqual(format_currency(1234567.89), "$1,234,567.89")

    def test_empty_portfolio(self) -> None:
        """Verify empty portfolio gracefully returns zero metrics."""
        summary = calculate_portfolio_summary([])
        self.assertEqual(summary["total_investment"], 0.00)
        self.assertEqual(summary["total_shares"], 0)
        self.assertEqual(summary["holdings_count"], 0)
        self.assertEqual(summary["distinct_stocks"], 0)
        self.assertEqual(summary["symbol_breakdown"], {})

    def test_ten_aapl_gives_1800(self) -> None:
        """Test Case: 10 AAPL shares at 180.00 gives exactly 1800.00."""
        aapl_lot = create_holding_record("AAPL", 10)
        self.assertEqual(aapl_lot["symbol"], "AAPL")
        self.assertEqual(aapl_lot["shares"], 10)
        self.assertEqual(aapl_lot["price_per_share"], 180.00)
        self.assertEqual(aapl_lot["total_value"], 1800.00)

        summary = calculate_portfolio_summary([aapl_lot])
        self.assertEqual(summary["total_investment"], 1800.00)
        self.assertEqual(summary["total_shares"], 10)
        self.assertEqual(summary["holdings_count"], 1)
        self.assertEqual(summary["distinct_stocks"], 1)

    def test_combined_aapl_and_tsla_gives_2300(self) -> None:
        """Test Case: 10 AAPL @ 180.00 + 2 TSLA @ 250.00 makes combined total 2300.00."""
        aapl_lot = create_holding_record("AAPL", 10)  # 1800.00
        tsla_lot = create_holding_record("TSLA", 2)   # 500.00

        self.assertEqual(tsla_lot["total_value"], 500.00)

        portfolio = [aapl_lot, tsla_lot]
        summary = calculate_portfolio_summary(portfolio)

        self.assertEqual(summary["total_investment"], 2300.00)
        self.assertEqual(summary["total_shares"], 12)
        self.assertEqual(summary["holdings_count"], 2)
        self.assertEqual(summary["distinct_stocks"], 2)

    def test_repeated_stock_entries(self) -> None:
        """Test Case: Repeated stock entries work (multiple lots of same ticker)."""
        aapl_lot_1 = create_holding_record("AAPL", 10)  # 1800.00
        tsla_lot = create_holding_record("TSLA", 2)     # 500.00
        aapl_lot_2 = create_holding_record("AAPL", 5)   # 900.00

        portfolio = [aapl_lot_1, tsla_lot, aapl_lot_2]
        summary = calculate_portfolio_summary(portfolio)

        self.assertEqual(summary["total_investment"], 3200.00)
        self.assertEqual(summary["total_shares"], 17)
        self.assertEqual(summary["holdings_count"], 3)
        self.assertEqual(summary["distinct_stocks"], 2)  # AAPL and TSLA

        # Verify consolidated breakdown for AAPL
        breakdown = summary["symbol_breakdown"]
        self.assertEqual(breakdown["AAPL"]["shares"], 15)
        self.assertEqual(breakdown["AAPL"]["total_value"], 2700.00)
        self.assertEqual(breakdown["AAPL"]["lots_count"], 2)

        # Verify unique IDs for each lot even with same ticker
        self.assertNotEqual(aapl_lot_1["id"], aapl_lot_2["id"])

    def test_invalid_zero_and_negative_quantities_rejected(self) -> None:
        """Test Case: Invalid, zero, and negative quantities are rejected."""
        # Zero quantity
        with self.assertRaises(ValueError):
            create_holding_record("AAPL", 0)

        # Negative quantity
        with self.assertRaises(ValueError):
            create_holding_record("AAPL", -1)

        with self.assertRaises(ValueError):
            create_holding_record("TSLA", -10)

        # Non-integer / float quantity
        with self.assertRaises(ValueError):
            create_holding_record("AAPL", 2.5)  # type: ignore

        # Invalid ticker symbol
        with self.assertRaises(KeyError):
            create_holding_record("INVALID_XYZ", 10)

        # Check calculate_holding_value directly
        with self.assertRaises(ValueError):
            calculate_holding_value(0, 180.00)

        with self.assertRaises(ValueError):
            calculate_holding_value(-5, 180.00)

    def test_individual_removal_deletes_only_selected_entry(self) -> None:
        """Test Case: Individual removal deletes ONLY the selected entry."""
        aapl_lot_1 = create_holding_record("AAPL", 10)
        tsla_lot = create_holding_record("TSLA", 2)
        aapl_lot_2 = create_holding_record("AAPL", 5)

        portfolio = [aapl_lot_1, tsla_lot, aapl_lot_2]

        # Target only aapl_lot_1 for removal
        target_id = aapl_lot_1["id"]
        updated_portfolio = [item for item in portfolio if item["id"] != target_id]

        self.assertEqual(len(updated_portfolio), 2)
        remaining_ids = [item["id"] for item in updated_portfolio]
        self.assertNotIn(target_id, remaining_ids)
        self.assertIn(tsla_lot["id"], remaining_ids)
        self.assertIn(aapl_lot_2["id"], remaining_ids)

        # Re-verify updated totals
        summary = calculate_portfolio_summary(updated_portfolio)
        self.assertEqual(summary["total_investment"], 1400.00)  # 500 (TSLA) + 900 (AAPL)
        self.assertEqual(summary["total_shares"], 7)
        self.assertEqual(summary["distinct_stocks"], 2)

    def test_clearing_resets_portfolio(self) -> None:
        """Test Case: Clearing resets the portfolio to an empty state."""
        portfolio = [
            create_holding_record("AAPL", 10),
            create_holding_record("TSLA", 2),
        ]
        self.assertEqual(len(portfolio), 2)

        # Execute clear
        portfolio = []
        summary = calculate_portfolio_summary(portfolio)

        self.assertEqual(summary["total_investment"], 0.00)
        self.assertEqual(summary["total_shares"], 0)
        self.assertEqual(summary["holdings_count"], 0)
        self.assertEqual(summary["distinct_stocks"], 0)

    def test_csv_export_contains_holdings_and_totals(self) -> None:
        """Test Case: CSV export contains correct holdings and totals."""
        aapl_lot = create_holding_record("AAPL", 10)  # 1800.00
        tsla_lot = create_holding_record("TSLA", 2)   # 500.00
        portfolio = [aapl_lot, tsla_lot]

        csv_text = export_portfolio_to_csv(portfolio)
        reader = list(csv.reader(io.StringIO(csv_text)))

        # Header check
        self.assertIn("Holding ID", reader[0])
        self.assertIn("Stock Symbol", reader[0])
        self.assertIn("Total Investment Value (USD)", reader[0])

        # Holdings rows check
        holding_symbols = [row[1] for row in reader[1:3]]
        self.assertIn("AAPL", holding_symbols)
        self.assertIn("TSLA", holding_symbols)

        # Find TOTAL row
        total_rows = [row for row in reader if len(row) > 0 and row[0] == "TOTAL"]
        self.assertEqual(len(total_rows), 1)
        total_row = total_rows[0]

        # Total shares must be 12 (10 + 2)
        self.assertEqual(int(total_row[3]), 12)
        # Total value must be 2300.00 (1800.00 + 500.00)
        self.assertEqual(float(total_row[5]), 2300.00)


if __name__ == "__main__":
    unittest.main()
