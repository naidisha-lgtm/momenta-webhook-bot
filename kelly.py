"""
Kelly Criterion Calculator for Trading Strategy

Usage:
    1. Backtest your strategy in TradingView
    2. Export trade list to CSV (Strategy Tester → List of Trades → Export)
    3. Run: python kelly.py trades.csv

Computes:
    - Win rate, payoff ratio, expectancy
    - Classic (binary) Kelly fraction, plus half and quarter Kelly
    - Optimal f (Ralph Vince): maximizes expected log growth over the
      empirical trade distribution, normalized by the largest loss
"""

import sys

import numpy as np
import pandas as pd


def load_trades_from_csv(filepath: str) -> np.ndarray:
    """Load per-trade P&L from a TradingView export CSV."""
    df = pd.read_csv(filepath)
    for col in ("Profit", "Profit/Loss", "P&L", "PnL"):
        if col in df.columns:
            values = pd.to_numeric(df[col], errors="coerce").dropna().values
            if len(values) == 0:
                raise ValueError(f"Column '{col}' has no numeric values")
            return values
    print("Available columns:", df.columns.tolist())
    raise ValueError("Could not find a Profit column in CSV")


def classic_kelly(trades: np.ndarray) -> dict:
    """Binary Kelly: f = p - q/b, where b = avg win / avg loss.

    Interpreted as the fraction of capital to RISK per trade, assuming a
    losing trade loses the full risked amount.
    """
    wins = trades[trades > 0]
    losses = trades[trades < 0]
    if len(wins) == 0 or len(losses) == 0:
        raise ValueError("Need at least one win and one loss to compute Kelly")

    p = len(wins) / len(trades)
    q = 1 - p
    b = wins.mean() / abs(losses.mean())
    f = p - q / b

    return {
        "num_trades": len(trades),
        "win_rate": p,
        "avg_win": wins.mean(),
        "avg_loss": losses.mean(),
        "payoff_ratio": b,
        "expectancy": trades.mean(),
        "kelly": f,
    }


def optimal_f(trades: np.ndarray) -> tuple[float, float]:
    """Ralph Vince optimal f: grid-search the f that maximizes mean log growth,
    where each trade's return is f * (pnl / |largest loss|).

    Returns (f, geometric mean growth per trade at that f).
    """
    worst = abs(trades.min())
    hprs_base = trades / worst  # holding-period returns per unit f
    best_f, best_g = 0.0, 0.0
    for f in np.arange(0.01, 1.0, 0.01):
        growth = 1 + f * hprs_base
        if (growth <= 0).any():
            break
        g = np.exp(np.mean(np.log(growth))) - 1
        if g > best_g:
            best_f, best_g = f, g
    return best_f, best_g


def main() -> None:
    filepath = sys.argv[1] if len(sys.argv) > 1 else "trades.csv"
    trades = load_trades_from_csv(filepath)

    stats = classic_kelly(trades)
    f_opt, growth = optimal_f(trades)

    print(f"Trades analyzed:     {stats['num_trades']}")
    print(f"Win rate:            {stats['win_rate']:.1%}")
    print(f"Avg win:             {stats['avg_win']:,.2f}")
    print(f"Avg loss:            {stats['avg_loss']:,.2f}")
    print(f"Payoff ratio (b):    {stats['payoff_ratio']:.2f}")
    print(f"Expectancy/trade:    {stats['expectancy']:,.2f}")
    print()
    print(f"Full Kelly:          {stats['kelly']:.1%} of capital risked per trade")
    print(f"Half Kelly:          {stats['kelly'] / 2:.1%}")
    print(f"Quarter Kelly:       {stats['kelly'] / 4:.1%}")
    print()
    print(f"Optimal f (Vince):   {f_opt:.1%} (geo growth/trade {growth:.2%})")
    print(f"Half optimal f:      {f_opt / 2:.1%}")
    print()
    print("Note: Kelly here is the fraction of capital RISKED per trade.")
    print("For long options, the max loss is the premium paid, so this is")
    print("the fraction of capital to allocate to premium per position.")


if __name__ == "__main__":
    main()
