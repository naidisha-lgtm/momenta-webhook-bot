"""
Monte Carlo Simulation for Trading Strategy
Analyzes risk and probability distribution of strategy outcomes

Usage:
    1. Backtest your strategy in TradingView
    2. Export trade list to CSV (Strategy Tester → List of Trades → Export)
    3. Run: python monte_carlo.py trades.csv

Or provide trades manually in the script below.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
import sys
from typing import List, Dict, Tuple

# ====================================
# CONFIGURATION
# ====================================

INITIAL_CAPITAL = 150000  # ₹1,50,000 (1.5 Lakhs)
NUM_SIMULATIONS = 10000   # Number of Monte Carlo runs
POSITION_SIZE_PCT = 100   # % of equity per trade (100 = full equity)
COMMISSION_PCT = 0.1      # 0.1% commission per trade
RISK_FREE_RATE = 0.06     # 6% annual risk-free rate (for Sharpe)

# ====================================
# TRADE DATA INPUT
# ====================================

def load_trades_from_csv(filepath: str) -> pd.DataFrame:
    """Load trades from TradingView export CSV"""
    try:
        df = pd.read_csv(filepath)
        # TradingView columns: Type, Signal, Date/Time, Contracts, Entry, Exit, Profit, %
        # We need the Profit column (in currency units)
        if 'Profit' in df.columns:
            return df['Profit'].values
        elif 'Profit/Loss' in df.columns:
            return df['Profit/Loss'].values
        else:
            print("Available columns:", df.columns.tolist())
            raise ValueError("Could not find Profit column in CSV")
    except FileNotFoundError:
        print(f"File not found: {filepath}")
        print("Using manual trade data instead...")
        return None

def manual_trade_data() -> np.ndarray:
    """
    Manual trade P&L data for testing
    Replace these with your actual backtest results

    Format: Array of profit/loss per trade in rupees
    Positive = profit, Negative = loss
    """
    # Example: 50 trades from a backtest
    # These are placeholder values - replace with your actual results
    trades = np.array([
        1200, -450, 890, 1500, -320, 670, -180, 1100, 450, -290,
        -520, 980, 1250, -410, 760, -150, 1400, 890, -380, 1050,
        -270, 1300, 650, -490, 1150, 780, -210, 950, -360, 1420,
        890, -330, 1080, 670, -190, 1250, 540, -450, 980, 1170,
        -280, 850, 1090, -370, 1310, 720, -240, 1160, 930, -410
    ])
    return trades

# ====================================
# MONTE CARLO SIMULATION
# ====================================

def run_monte_carlo(trades: np.ndarray,
                    initial_capital: float,
                    num_simulations: int,
                    position_size_pct: float = 100) -> Dict:
    """
    Run Monte Carlo simulation by randomly sampling trades with replacement

    Returns distribution of final equity, drawdowns, and risk metrics
    """

    num_trades = len(trades)
    results = {
        'final_equity': [],
        'max_drawdown': [],
        'max_drawdown_pct': [],
        'total_return_pct': [],
        'sharpe_ratio': [],
        'win_rate': [],
        'profit_factor': [],
        'largest_loss': [],
        'largest_win': [],
        'consecutive_losses': [],
        'went_bust': 0
    }

    print(f"\nRunning {num_simulations:,} Monte Carlo simulations...")
    print(f"Initial Capital: ₹{initial_capital:,.2f}")
    print(f"Number of trades per simulation: {num_trades}")
    print(f"Position size: {position_size_pct}% of equity\n")

    for sim in range(num_simulations):
        # Randomly sample trades with replacement (bootstrap)
        sampled_trades = np.random.choice(trades, size=num_trades, replace=True)

        # Simulate equity curve
        equity = initial_capital
        equity_curve = [equity]
        peak_equity = equity
        max_dd = 0
        max_dd_pct = 0
        consecutive_losses = 0
        max_consecutive_losses = 0

        wins = []
        losses = []

        for trade_pnl in sampled_trades:
            # Calculate position size (can be fixed or % of equity)
            position_value = equity * (position_size_pct / 100)

            # Apply trade P&L (scaled if using % position sizing)
            # If position_size_pct < 100, scale the P&L proportionally
            scaled_pnl = trade_pnl * (position_size_pct / 100)

            equity += scaled_pnl
            equity_curve.append(equity)

            # Track peak and drawdown
            if equity > peak_equity:
                peak_equity = equity

            dd = peak_equity - equity
            dd_pct = (dd / peak_equity) * 100 if peak_equity > 0 else 0

            if dd > max_dd:
                max_dd = dd
            if dd_pct > max_dd_pct:
                max_dd_pct = dd_pct

            # Track wins/losses
            if scaled_pnl > 0:
                wins.append(scaled_pnl)
                consecutive_losses = 0
            else:
                losses.append(abs(scaled_pnl))
                consecutive_losses += 1
                if consecutive_losses > max_consecutive_losses:
                    max_consecutive_losses = consecutive_losses

            # Check for bust (equity <= 0)
            if equity <= 0:
                results['went_bust'] += 1
                break

        # Calculate final metrics for this simulation
        final_equity = max(equity, 0)
        total_return_pct = ((final_equity - initial_capital) / initial_capital) * 100

        # Win rate
        total_trades = len(wins) + len(losses)
        win_rate = (len(wins) / total_trades * 100) if total_trades > 0 else 0

        # Profit factor
        gross_profit = sum(wins) if wins else 0
        gross_loss = sum(losses) if losses else 1  # avoid division by zero
        profit_factor = gross_profit / gross_loss if gross_loss > 0 else 0

        # Sharpe ratio (simplified - using trade returns)
        if len(equity_curve) > 1:
            returns = np.diff(equity_curve) / equity_curve[:-1]
            sharpe = np.mean(returns) / np.std(returns) * np.sqrt(252) if np.std(returns) > 0 else 0
        else:
            sharpe = 0

        # Store results
        results['final_equity'].append(final_equity)
        results['max_drawdown'].append(max_dd)
        results['max_drawdown_pct'].append(max_dd_pct)
        results['total_return_pct'].append(total_return_pct)
        results['sharpe_ratio'].append(sharpe)
        results['win_rate'].append(win_rate)
        results['profit_factor'].append(profit_factor)
        results['largest_loss'].append(max(losses) if losses else 0)
        results['largest_win'].append(max(wins) if wins else 0)
        results['consecutive_losses'].append(max_consecutive_losses)

        # Progress indicator
        if (sim + 1) % 1000 == 0:
            print(f"  Completed {sim + 1:,} / {num_simulations:,} simulations")

    return results

# ====================================
# ANALYSIS & REPORTING
# ====================================

def analyze_results(results: Dict, initial_capital: float) -> None:
    """Print detailed statistical analysis of Monte Carlo results"""

    print("\n" + "="*60)
    print("MONTE CARLO SIMULATION RESULTS")
    print("="*60)

    # Final Equity Distribution
    final_equity = np.array(results['final_equity'])
    print(f"\n📊 FINAL EQUITY DISTRIBUTION (₹)")
    print(f"   Best Case (95th %ile):     ₹{np.percentile(final_equity, 95):,.2f}")
    print(f"   75th Percentile:           ₹{np.percentile(final_equity, 75):,.2f}")
    print(f"   Median (50th %ile):        ₹{np.percentile(final_equity, 50):,.2f}")
    print(f"   Mean (Average):            ₹{np.mean(final_equity):,.2f}")
    print(f"   25th Percentile:           ₹{np.percentile(final_equity, 25):,.2f}")
    print(f"   Worst Case (5th %ile):     ₹{np.percentile(final_equity, 5):,.2f}")

    # Return Distribution
    returns = np.array(results['total_return_pct'])
    print(f"\n📈 RETURN DISTRIBUTION (%)")
    print(f"   Best Case (95th %ile):     {np.percentile(returns, 95):.2f}%")
    print(f"   75th Percentile:           {np.percentile(returns, 75):.2f}%")
    print(f"   Median:                    {np.percentile(returns, 50):.2f}%")
    print(f"   Mean:                      {np.mean(returns):.2f}%")
    print(f"   25th Percentile:           {np.percentile(returns, 25):.2f}%")
    print(f"   Worst Case (5th %ile):     {np.percentile(returns, 5):.2f}%")

    # Probability of Profit
    profitable_sims = sum(1 for r in returns if r > 0)
    prob_profit = (profitable_sims / len(returns)) * 100
    print(f"\n💰 PROBABILITY OF PROFIT")
    print(f"   Profitable simulations:    {profitable_sims:,} / {len(returns):,}")
    print(f"   Probability:               {prob_profit:.2f}%")

    # Risk of Ruin
    bust_pct = (results['went_bust'] / len(results['final_equity'])) * 100
    print(f"\n⚠️  RISK OF RUIN")
    print(f"   Went bust (equity ≤ 0):    {results['went_bust']:,} / {len(results['final_equity']):,}")
    print(f"   Probability:               {bust_pct:.2f}%")

    # Drawdown Analysis
    max_dd = np.array(results['max_drawdown'])
    max_dd_pct = np.array(results['max_drawdown_pct'])
    print(f"\n📉 MAXIMUM DRAWDOWN")
    print(f"   Worst DD (95th %ile):      ₹{np.percentile(max_dd, 95):,.2f} ({np.percentile(max_dd_pct, 95):.2f}%)")
    print(f"   Median DD:                 ₹{np.percentile(max_dd, 50):,.2f} ({np.percentile(max_dd_pct, 50):.2f}%)")
    print(f"   Best DD (5th %ile):        ₹{np.percentile(max_dd, 5):,.2f} ({np.percentile(max_dd_pct, 5):.2f}%)")

    # Performance Metrics
    print(f"\n📊 PERFORMANCE METRICS")
    print(f"   Median Win Rate:           {np.median(results['win_rate']):.2f}%")
    print(f"   Median Profit Factor:      {np.median(results['profit_factor']):.2f}")
    print(f"   Median Sharpe Ratio:       {np.median(results['sharpe_ratio']):.2f}")

    # Risk Metrics
    print(f"\n⚡ RISK METRICS")
    print(f"   Median Largest Loss:       ₹{np.median(results['largest_loss']):,.2f}")
    print(f"   Median Largest Win:        ₹{np.median(results['largest_win']):,.2f}")
    print(f"   Median Max Consecutive Losses: {int(np.median(results['consecutive_losses']))}")

    # Capital Requirements
    print(f"\n💵 CAPITAL REQUIREMENTS")
    min_equity = np.percentile(final_equity, 5)
    recommended_capital = initial_capital / (1 - np.percentile(max_dd_pct, 95)/100)
    print(f"   Initial Capital:           ₹{initial_capital:,.2f}")
    print(f"   Recommended Capital (to survive 95th %ile DD): ₹{recommended_capital:,.2f}")

    print("\n" + "="*60)

def plot_results(results: Dict, initial_capital: float) -> None:
    """Create visualization plots of Monte Carlo results"""

    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    fig.suptitle(f'Monte Carlo Simulation Results (₹{initial_capital:,.0f} Initial Capital)',
                 fontsize=16, fontweight='bold')

    # Plot 1: Final Equity Distribution
    ax1 = axes[0, 0]
    final_equity = results['final_equity']
    ax1.hist(final_equity, bins=50, color='steelblue', alpha=0.7, edgecolor='black')
    ax1.axvline(initial_capital, color='red', linestyle='--', linewidth=2, label='Initial Capital')
    ax1.axvline(np.median(final_equity), color='green', linestyle='--', linewidth=2, label='Median')
    ax1.set_xlabel('Final Equity (₹)')
    ax1.set_ylabel('Frequency')
    ax1.set_title('Final Equity Distribution')
    ax1.legend()
    ax1.grid(alpha=0.3)

    # Plot 2: Return Distribution
    ax2 = axes[0, 1]
    returns = results['total_return_pct']
    ax2.hist(returns, bins=50, color='coral', alpha=0.7, edgecolor='black')
    ax2.axvline(0, color='red', linestyle='--', linewidth=2, label='Break-even')
    ax2.axvline(np.median(returns), color='green', linestyle='--', linewidth=2, label='Median')
    ax2.set_xlabel('Total Return (%)')
    ax2.set_ylabel('Frequency')
    ax2.set_title('Return Distribution')
    ax2.legend()
    ax2.grid(alpha=0.3)

    # Plot 3: Drawdown Distribution
    ax3 = axes[1, 0]
    max_dd_pct = results['max_drawdown_pct']
    ax3.hist(max_dd_pct, bins=50, color='crimson', alpha=0.7, edgecolor='black')
    ax3.axvline(np.median(max_dd_pct), color='yellow', linestyle='--', linewidth=2, label='Median')
    ax3.set_xlabel('Maximum Drawdown (%)')
    ax3.set_ylabel('Frequency')
    ax3.set_title('Maximum Drawdown Distribution')
    ax3.legend()
    ax3.grid(alpha=0.3)

    # Plot 4: Probability Curve
    ax4 = axes[1, 1]
    sorted_returns = np.sort(returns)
    probabilities = np.arange(1, len(sorted_returns) + 1) / len(sorted_returns) * 100
    ax4.plot(sorted_returns, probabilities, linewidth=2, color='darkgreen')
    ax4.axvline(0, color='red', linestyle='--', linewidth=1, label='Break-even')
    ax4.axhline(50, color='gray', linestyle='--', linewidth=1, alpha=0.5)
    ax4.set_xlabel('Total Return (%)')
    ax4.set_ylabel('Probability (%)')
    ax4.set_title('Cumulative Probability of Return')
    ax4.legend()
    ax4.grid(alpha=0.3)

    plt.tight_layout()
    plt.savefig('monte_carlo_results.png', dpi=150, bbox_inches='tight')
    print("\n📊 Charts saved to: monte_carlo_results.png")
    plt.show()

# ====================================
# MAIN EXECUTION
# ====================================

def main():
    """Main execution function"""

    # Load trade data
    if len(sys.argv) > 1:
        # CSV file provided as command line argument
        csv_file = sys.argv[1]
        trades = load_trades_from_csv(csv_file)
        if trades is None:
            trades = manual_trade_data()
    else:
        # Use manual trade data
        print("No CSV file provided. Using manual trade data.")
        print("To use TradingView export: python monte_carlo.py trades.csv\n")
        trades = manual_trade_data()

    print(f"Loaded {len(trades)} trades")
    print(f"Average trade P&L: ₹{np.mean(trades):.2f}")
    print(f"Win rate: {(sum(1 for t in trades if t > 0) / len(trades) * 100):.2f}%")

    # Run Monte Carlo simulation
    results = run_monte_carlo(
        trades=trades,
        initial_capital=INITIAL_CAPITAL,
        num_simulations=NUM_SIMULATIONS,
        position_size_pct=POSITION_SIZE_PCT
    )

    # Analyze and report results
    analyze_results(results, INITIAL_CAPITAL)

    # Generate plots
    try:
        plot_results(results, INITIAL_CAPITAL)
    except Exception as e:
        print(f"\n⚠️  Could not generate plots: {e}")
        print("Install matplotlib to see visual charts: pip install matplotlib")

    print("\n✅ Monte Carlo simulation complete!")

if __name__ == "__main__":
    main()
