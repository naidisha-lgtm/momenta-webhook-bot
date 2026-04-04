# Monte Carlo Simulation Guide

## Overview

Monte Carlo simulation tests your strategy's robustness by running thousands of randomized trade sequences. This shows you the **probability distribution** of outcomes rather than a single historical backtest path.

**Why Monte Carlo?**
- Historical backtest = 1 path through time (what happened)
- Monte Carlo = 10,000 possible paths (what could happen)
- Reveals true risk: worst cases, probability of ruin, confidence intervals

---

## Quick Start

### 1. Backtest in TradingView

1. Add `pa_momentum_strategy.pine` to your ETH/USD chart
2. Select timeframe (recommend 1h or 4h)
3. Let strategy run on historical data
4. Open "Strategy Tester" tab at bottom

### 2. Export Trade Data

In Strategy Tester:
1. Click "List of Trades" tab
2. Click download icon (top right)
3. Save as `trades.csv`
4. Move file to this folder

### 3. Run Monte Carlo Simulation

```bash
# Install dependencies first
pip install numpy pandas matplotlib

# Run simulation
python monte_carlo.py trades.csv
```

**Or use manual test data:**
```bash
python monte_carlo.py
```

---

## What the Simulation Does

### Process

1. **Loads your trades** (e.g., 50 trades from backtest)
2. **Randomly reorders them** 10,000 times
   - Simulation #1: trades in order [3, 47, 12, 8, ...]
   - Simulation #2: trades in order [21, 5, 39, 44, ...]
   - etc. for 10,000 iterations
3. **Calculates outcomes** for each path
   - Final equity
   - Maximum drawdown
   - Win rate
   - Profit factor
   - Risk of ruin (going bust)
4. **Shows probability distribution**

### Why Random Order?

Markets are random. Just because trade #5 came after trade #4 historically doesn't mean it will next time. By shuffling trades, we simulate different market sequences.

---

## Understanding the Results

### 📊 Final Equity Distribution

```
Best Case (95th %ile):     ₹2,45,000
75th Percentile:           ₹2,10,000
Median (50th %ile):        ₹1,85,000
Mean (Average):            ₹1,88,500
25th Percentile:           ₹1,62,000
Worst Case (5th %ile):     ₹1,35,000
```

**What this means:**
- **Median**: 50% chance you end above ₹1,85,000, 50% below
- **95th percentile**: Only 5% of simulations did better (best realistic case)
- **5th percentile**: Only 5% of simulations did worse (worst realistic case)

**How to use it:**
- Plan for the 25th percentile, not the median
- If 5th percentile is below your risk tolerance, reduce position size

### 📈 Return Distribution

```
Best Case (95th %ile):     +63.3%
Median:                    +23.3%
Worst Case (5th %ile):     -10.0%
```

**What this means:**
- There's a 50% chance you'll return more than 23.3%
- There's a 5% chance you could lose 10%
- Best case scenario is +63%, but rare

### 💰 Probability of Profit

```
Profitable simulations:    8,234 / 10,000
Probability:               82.34%
```

**What this means:**
- 82.34% chance the strategy will be profitable over this trade sequence
- 17.66% chance it will lose money
- Higher % = more robust strategy

**Target**: > 75% for a good strategy

### ⚠️ Risk of Ruin

```
Went bust (equity ≤ 0):    12 / 10,000
Probability:               0.12%
```

**What this means:**
- 0.12% chance of losing all capital
- Very low = safe
- High % = reduce position size immediately

**Target**: < 1% (ideally < 0.1%)

### 📉 Maximum Drawdown

```
Worst DD (95th %ile):      ₹35,000 (23.3%)
Median DD:                 ₹18,500 (12.3%)
Best DD (5th %ile):        ₹8,200 (5.5%)
```

**What this means:**
- Median case: You'll likely see a -12.3% drawdown at some point
- Worst case: In bad luck, could see -23.3% drawdown
- This is how much capital drops from peak to trough

**How to use it:**
- Ensure you can stomach the 95th percentile DD psychologically
- If 95th %ile DD is -50%, you'll likely panic and quit
- Keep DD under 25-30% for sustainable trading

### 📊 Performance Metrics

```
Median Win Rate:           52.5%
Median Profit Factor:      1.65
Median Sharpe Ratio:       1.12
```

**What this means:**
- **Win Rate**: You'll win about 52.5% of trades (slightly above 50/50)
- **Profit Factor**: You make ₹1.65 for every ₹1 you lose (good if > 1.5)
- **Sharpe Ratio**: Risk-adjusted returns (good if > 1.0)

### ⚡ Risk Metrics

```
Median Largest Loss:       ₹4,200
Median Largest Win:        ₹8,500
Median Max Consecutive Losses: 5
```

**What this means:**
- Your worst single trade will likely be around -₹4,200
- Your best single trade will likely be around +₹8,500
- You'll likely face 5 losses in a row at some point

**How to use it:**
- Can you handle 5 losses in a row without quitting?
- Is ₹4,200 loss per trade acceptable?

### 💵 Capital Requirements

```
Initial Capital:                              ₹1,50,000
Recommended Capital (to survive 95th %ile DD): ₹1,95,000
```

**What this means:**
- You're starting with ₹1,50,000
- To safely survive worst-case DD, you'd need ₹1,95,000
- Consider this when sizing positions

---

## Configuration Options

Edit `monte_carlo.py` at the top:

```python
INITIAL_CAPITAL = 150000    # Starting equity (₹)
NUM_SIMULATIONS = 10000     # More = more accurate (slower)
POSITION_SIZE_PCT = 100     # % of equity per trade
COMMISSION_PCT = 0.1        # Commission per trade
```

### Position Size Impact

**100% of equity** (default):
- Applies full trade P&L from backtest
- Assumes you're fully invested each trade
- Higher returns, higher risk

**50% of equity**:
- Halves all trade P&L
- More conservative, lower drawdowns
- Slower account growth

**25% of equity**:
- Quarters all trade P&L
- Very conservative
- Good for testing risk management

### Number of Simulations

- **1,000**: Quick test, less accurate
- **10,000**: Standard (recommended)
- **100,000**: Very accurate, slow (~1 minute)

---

## Visual Charts

The script generates 4 charts saved to `monte_carlo_results.png`:

### 1. Final Equity Distribution (Histogram)
Shows the range of possible final equity values.
- X-axis: Final equity amount
- Y-axis: How many simulations ended at this level
- Red line: Starting capital (break-even)
- Green line: Median outcome

### 2. Return Distribution (Histogram)
Shows the range of possible returns as percentages.
- X-axis: Total return %
- Y-axis: Frequency
- Red line: 0% (break-even)
- Green line: Median return

### 3. Maximum Drawdown Distribution (Histogram)
Shows how bad drawdowns can get.
- X-axis: Max drawdown %
- Y-axis: Frequency
- Yellow line: Median drawdown

### 4. Cumulative Probability Curve
Shows the probability of achieving each return level.
- X-axis: Return %
- Y-axis: Probability of getting that return or less
- Example: If curve crosses 0% return at 20% probability, there's a 20% chance of losing money

---

## Using Results to Improve Strategy

### If Risk of Ruin > 1%
**Problem**: Too risky, could blow up account

**Solutions**:
- Reduce position size (100% → 50% or 25%)
- Increase initial capital
- Tighten ATR stop (0.5 → 0.3)
- Filter out low-probability trades

### If Max Drawdown > 30%
**Problem**: Psychologically difficult to trade

**Solutions**:
- Reduce position size
- Widen ATR stop (fewer stop-outs)
- Add filters (only trade with HTF trend)
- Increase win rate (tighter entry criteria)

### If Probability of Profit < 70%
**Problem**: Strategy not robust enough

**Solutions**:
- Check if edge exists (profit factor > 1.5?)
- More trades needed (extend backtest period)
- Optimize parameters (swing lookback, ATR multiplier)
- Consider different timeframe

### If Median Return < 15% annually
**Problem**: Returns too low for risk taken

**Solutions**:
- Increase position size (if drawdown allows)
- Trade more frequently (lower timeframe)
- Optimize exits (let winners run more)
- Stack multiple strategies

---

## Interpreting Example Results

### Scenario A: Aggressive Strategy
```
Initial Capital:           ₹1,50,000
Median Final Equity:       ₹2,50,000 (+66%)
5th Percentile:            ₹80,000 (-46%)
Probability of Profit:     65%
Max DD (95th %ile):        -55%
Risk of Ruin:              2.5%
```

**Analysis**:
- ❌ High risk of ruin (2.5% is too high)
- ❌ Max DD of -55% is psychologically unsustainable
- ✅ Good median return (+66%)
- ⚠️ Only 65% probability of profit (marginal)

**Recommendation**: Reduce position size by 50% or increase capital to ₹3,00,000

### Scenario B: Conservative Strategy
```
Initial Capital:           ₹1,50,000
Median Final Equity:       ₹1,75,000 (+16%)
5th Percentile:            ₹1,40,000 (-6%)
Probability of Profit:     88%
Max DD (95th %ile):        -15%
Risk of Ruin:              0.02%
```

**Analysis**:
- ✅ Very low risk of ruin
- ✅ Manageable max DD (-15%)
- ✅ High probability of profit (88%)
- ⚠️ Lower returns (+16% median)

**Recommendation**: This is tradeable. Consider increasing position size slightly if comfortable with risk.

### Scenario C: Ideal Strategy
```
Initial Capital:           ₹1,50,000
Median Final Equity:       ₹2,10,000 (+40%)
5th Percentile:            ₹1,35,000 (-10%)
Probability of Profit:     82%
Max DD (95th %ile):        -22%
Risk of Ruin:              0.08%
```

**Analysis**:
- ✅ Very low risk of ruin
- ✅ Manageable max DD (-22%)
- ✅ Strong probability of profit (82%)
- ✅ Good median return (+40%)

**Recommendation**: Trade this! Good risk/reward balance.

---

## Advanced: Manual Trade Input

If you don't have TradingView Pro (can't export trades), manually enter your backtest results:

Edit `monte_carlo.py` in the `manual_trade_data()` function:

```python
def manual_trade_data() -> np.ndarray:
    trades = np.array([
        1200,   # Trade 1: +₹1,200 profit
        -450,   # Trade 2: -₹450 loss
        890,    # Trade 3: +₹890 profit
        # ... add all your trades here
    ])
    return trades
```

Get trade P&L from:
- Strategy Tester → List of Trades → "Profit" column
- Manually note down each trade result
- Enter into array (comma-separated)

---

## Troubleshooting

### "Module not found: numpy"
```bash
pip install numpy pandas matplotlib
```

### "File not found: trades.csv"
- Make sure CSV is in same folder as `monte_carlo.py`
- Check filename spelling
- Or use manual trade data (no CSV needed)

### "Could not generate plots"
```bash
pip install matplotlib
```

### Results seem unrealistic
- Check that POSITION_SIZE_PCT matches your actual trading
- Verify COMMISSION_PCT matches your broker
- Ensure trades.csv has actual P&L values (not percentages)

### Want faster simulations
- Reduce NUM_SIMULATIONS from 10,000 to 1,000
- Less accurate but much faster

---

## Next Steps

1. **Run simulation** on your backtest
2. **Analyze results** — focus on risk of ruin and max DD
3. **Adjust position sizing** if needed
4. **Re-run simulation** with new parameters
5. **Iterate** until risk metrics are acceptable
6. **Paper trade** for 2-4 weeks
7. **Go live** with small size
8. **Run Monte Carlo monthly** as you accumulate more trade data

---

## FAQ

**Q: How many trades do I need for accurate Monte Carlo?**
A: Minimum 30, ideally 50+. More trades = more accurate simulation.

**Q: Should I run this on every backtest?**
A: Yes. Always run Monte Carlo before live trading any strategy.

**Q: What if my probability of profit is only 60%?**
A: That means 40% chance of loss. Improve the strategy or don't trade it.

**Q: Can I use this for options trading?**
A: Yes, but P&L should reflect actual option premium profits/losses, not underlying price changes.

**Q: How often should I update the simulation?**
A: Re-run monthly as you gather more real trade data. Stop if risk metrics deteriorate.

**Q: What's a good risk of ruin %?**
A: Under 1% is good, under 0.1% is excellent. Above 5% is too risky.

---

*Monte Carlo simulation is a statistical technique — it shows probabilities, not guarantees. Past performance (even randomized) doesn't guarantee future results.*
