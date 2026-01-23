# TradingView Strategy Setup Guide

## Overview
This guide explains the "2 Same Color Heikin Ashi Strategy" with ATR trailing stop loss. This is a complete backtestable strategy with separate entry/exit webhooks.

---

## Strategy Logic

### Entry Signals
- **LONG Entry**: 2 consecutive green (bullish) Heikin Ashi candles
- **SHORT Entry**: 2 consecutive red (bearish) Heikin Ashi candles
- Entry occurs on bar close when pattern is confirmed (no repaint)

### Exit Signals
The strategy has **TWO exit mechanisms**:

1. **Opposite Signal Exit**
   - LONG exits when 2 red HA candles form
   - SHORT exits when 2 green HA candles form
   - This is the "next candle" exit you requested

2. **ATR Trailing Stop Loss (0.5x ATR)**
   - Calculated as: Current Price ± (ATR × 0.5)
   - Trails in favorable direction only (never worse)
   - Protects profits while letting winners run
   - Triggers if price hits stop level

### Key Features

**No Repaint Guarantee:**
- All signals confirmed on bar close only
- Uses `barstate.isconfirmed` throughout
- Historical backtest = real-time performance

**Risk Management:**
- 0.5 ATR trailing stop (configurable)
- Position sizing: 100% equity (configurable)
- Commission: 0.1% per trade (configurable)

**Webhook Integration:**
- Separate messages for entry and exit
- Includes action type and reason
- JSON format compatible with webhook bot

---

## Webhook Messages

### Entry Messages

**LONG Entry:**
```json
{"signal":"LONG","action":"entry"}
```

**SHORT Entry:**
```json
{"signal":"SHORT","action":"entry"}
```

### Exit Messages

**LONG Exit (Opposite Signal):**
```json
{"signal":"LONG","action":"exit","reason":"opposite_signal"}
```

**LONG Exit (Trailing Stop):**
```json
{"signal":"LONG","action":"exit","reason":"trailing_stop"}
```

**SHORT Exit (Opposite Signal):**
```json
{"signal":"SHORT","action":"exit","reason":"opposite_signal"}
```

**SHORT Exit (Trailing Stop):**
```json
{"signal":"SHORT","action":"exit","reason":"trailing_stop"}
```

---

## Installation Steps

### 1. Add Strategy to TradingView

1. Open TradingView and go to any chart
2. Click "Pine Editor" at the bottom
3. Click "New" → "Strategy"
4. Copy entire contents of `heikin_ashi_strategy.pine`
5. Paste into Pine Editor
6. Click "Save" and name it (e.g., "2 Same HA Strategy")
7. Click "Add to Chart"

### 2. Configure Strategy Settings

Click the gear icon next to the strategy name to access settings:

#### Properties Tab
- **Initial Capital**: $10,000 (default, adjust as needed)
- **Order Size**: 100% of equity (or set fixed quantity)
- **Commission**: 0.1% per trade
- **Slippage**: 0 ticks (adjust for crypto/forex)
- **Pyramiding**: 0 (one position at a time)
- **Recalculate**: After order is filled

#### Inputs Tab

**Display Settings:**
- Show Heikin Ashi Candles: OFF (recommended)
- Show Stop Loss Lines: ON (visualize trailing stops)

**Risk Management:**
- ATR Length: 14 (default, standard ATR period)
- ATR Multiplier for TSL: 0.5 (half ATR distance for stops)

**Strategy Logic:**
- Exit on Opposite Signal: ON (exit when opposite pattern appears)
- Use ATR Trailing Stop: ON (enable trailing stop protection)

### 3. Set Up Alerts for Live Trading

For automated webhook trading, you need **ONE alert** that captures all signals:

#### Combined Alert (Recommended)

1. Right-click on chart → "Add alert"
2. **Condition**: Select your strategy name → "Order fills only"
3. **Alert name**: "HA Strategy - All Orders"
4. **Frequency**: "Once Per Bar Close"
5. **Message**: Use placeholder `{{strategy.order.alert_message}}`
   - This will automatically use the custom messages from the strategy
6. **Webhook URL**: `http://your-server:10000/webhook`
7. **Expiration**: Open-ended
8. Click "Create"

**Important**: The `{{strategy.order.alert_message}}` placeholder will be replaced with the JSON messages defined in the strategy code.

#### Alternative: Separate Alerts (More Control)

If you want separate webhooks for entries vs exits:

**Entry Alert:**
1. Condition: Strategy → "Order fills only"
2. Filter to only entry orders (manually, by testing)
3. Message: `{"signal":"{{strategy.order.action}}","action":"entry"}`
4. Webhook URL: `http://your-server:10000/webhook/entry`

**Exit Alert:**
1. Condition: Strategy → "Order fills only"
2. Filter to only exit orders
3. Message: `{"signal":"{{strategy.order.action}}","action":"exit"}`
4. Webhook URL: `http://your-server:10000/webhook/exit`

---

## Backtesting the Strategy

### How to Backtest

1. Add strategy to chart
2. Select timeframe (recommended: 15m, 1h, 4h)
3. Select asset (ETH/USD for your bot)
4. View performance in "Strategy Tester" tab at bottom

### Key Metrics to Evaluate

**Overview Tab:**
- **Net Profit**: Total profit/loss in $
- **Total Closed Trades**: Number of completed trades
- **Percent Profitable**: Win rate (aim for >50%)
- **Profit Factor**: Gross profit ÷ Gross loss (aim for >1.5)
- **Max Drawdown**: Largest peak-to-trough loss (lower is better)
- **Avg Trade**: Average profit per trade

**Performance Summary:**
- **Sharpe Ratio**: Risk-adjusted returns (higher is better)
- **Sortino Ratio**: Downside risk-adjusted returns
- **Win/Loss Ratio**: Average win ÷ Average loss (aim for >1.5)

**Trade Analysis:**
- Check "List of Trades" to see all entries/exits
- Identify patterns in losing trades
- Adjust ATR multiplier if stops are too tight/loose

### Optimization Tips

**If too many losses:**
- Increase ATR multiplier (0.5 → 0.75 or 1.0)
- This gives trades more room to breathe
- But also increases max loss per trade

**If profits run then give back:**
- Decrease ATR multiplier (0.5 → 0.3 or 0.4)
- This locks in profits sooner
- But may exit winning trades early

**If not enough trades:**
- Try different timeframes (5m for more, 4h for less)
- Strategy is timeframe-agnostic

**If too many whipsaws:**
- Consider adding filter (RSI, volume, etc.)
- Or increase minimum HA candle size requirement

---

## Understanding the ATR Trailing Stop

### What is ATR?
Average True Range measures volatility over the last N periods (default 14).

### How the Trailing Stop Works

**For LONG positions:**
1. Entry: Stop placed at `Entry Price - (ATR × 0.5)`
2. Price rises: Stop trails up to `Current Price - (ATR × 0.5)`
3. Price falls: Stop stays at highest level (doesn't move down)
4. Exit: When price hits stop OR opposite signal appears

**For SHORT positions:**
1. Entry: Stop placed at `Entry Price + (ATR × 0.5)`
2. Price falls: Stop trails down to `Current Price + (ATR × 0.5)`
3. Price rises: Stop stays at lowest level (doesn't move up)
4. Exit: When price hits stop OR opposite signal appears

### Example

**ETH at $3,000, ATR = 100**

LONG entry:
- Initial stop: $3,000 - (100 × 0.5) = $2,950
- Price rises to $3,100: Stop moves to $3,050
- Price rises to $3,200: Stop moves to $3,150
- Price falls to $3,180: Stop stays at $3,150 (doesn't drop)
- If price hits $3,150 → Exit via trailing stop

**Adjusting the Multiplier:**
- 0.5 (default): Tight stop, more exits, less profit per trade
- 1.0: Medium stop, balanced
- 2.0: Wide stop, fewer exits, more profit per trade (but bigger losses)

---

## Visual Indicators on Chart

### Entry Signals
- **Green Triangle Up + "LONG ENTRY"**: Long position opened
- **Red Triangle Down + "SHORT ENTRY"**: Short position opened
- **Green Background**: Long entry bar
- **Red Background**: Short entry bar

### Exit Signals
- **Orange X + "EXIT"**: Opposite signal exit triggered
- Exit via trailing stop has no marker (shown in trade list)

### Stop Loss Lines
- **Red Line**: Current trailing stop level
- Only visible when position is open
- Updates each bar as price moves favorably

### Pattern Detection
- **Light Green Background**: 2 green HA candles pattern active
- **Light Red Background**: 2 red HA candles pattern active
- Shows when condition is met (even if no position)

### Dashboard (Top Right)
- **Position**: Current position (LONG/SHORT/Flat)
- **HA Pattern**: Current Heikin Ashi pattern state
- **ATR**: Current ATR value
- **Stop Distance**: Current stop distance (ATR × multiplier)
- **Stop Level**: Actual price level of stop
- **Bar Status**: Closed ✓ or In Progress...

### Performance Label (Top Right of Last Bar)
- **Trades**: Total closed trades
- **Win Rate**: Percentage of winning trades
- **Profit Factor**: Ratio of gross profit to gross loss
- **Net P&L**: Total profit/loss

---

## Webhook Bot Integration

### Update Your Flask Webhook Bot

Your current bot (`app.py`) expects simple `{"signal":"LONG"}` or `{"signal":"SHORT"}`.

For the strategy, you need to handle entry/exit actions. Here's how to modify:

#### Option 1: Simple Approach (Entry Only)

Keep existing bot logic, only trade on entries, ignore exits:

```python
signal = data.get("signal")
action = data.get("action", "entry")

if action == "entry":
    # Your existing logic
    if signal == "LONG":
        # Select call option
    elif signal == "SHORT":
        # Select put option
elif action == "exit":
    # Close the position (future implementation)
    print(f"🚫 EXIT signal received, closing {signal} position")
```

#### Option 2: Full Entry/Exit Tracking

Track open positions and close them on exit signals:

```python
# Global position tracker (in production use database)
current_position = {"type": None, "option": None}

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    signal = data.get("signal")
    action = data.get("action")
    reason = data.get("reason", "unknown")

    if action == "entry":
        # Open new position
        if signal == "LONG":
            option = pick_call_option()  # Your existing logic
            current_position = {"type": "LONG", "option": option}
            print(f"✅ LONG ENTRY: {option}")
            # Send to Delta Exchange API (when ready)

        elif signal == "SHORT":
            option = pick_put_option()  # Your existing logic
            current_position = {"type": "SHORT", "option": option}
            print(f"✅ SHORT ENTRY: {option}")
            # Send to Delta Exchange API (when ready)

    elif action == "exit":
        # Close existing position
        if current_position["type"] is not None:
            print(f"🚫 EXIT: Closing {current_position['type']} position")
            print(f"   Reason: {reason}")
            # Send close order to Delta Exchange API (when ready)
            current_position = {"type": None, "option": None}
        else:
            print("⚠️ EXIT signal but no position open")

    return jsonify({"status": "ok"}), 200
```

---

## Testing Procedure

### 1. Backtest First

Before live trading:
1. Load strategy on ETH/USD chart
2. Set timeframe (15m or 1h recommended)
3. Run backtest on 3-6 months of data
4. Check metrics:
   - Profit Factor > 1.5?
   - Win Rate > 45%?
   - Max Drawdown acceptable?
5. Optimize ATR multiplier if needed
6. Re-run backtest to confirm

### 2. Paper Trade

1. Set up alerts with webhook
2. Run Flask app locally
3. Monitor console for webhook messages
4. Verify entry/exit signals match chart
5. Track simulated P&L in spreadsheet
6. Run for 1-2 weeks minimum

### 3. Live Trading (Small Size)

1. Update bot to execute real trades
2. Start with minimum position size
3. Monitor first 5-10 trades closely
4. Verify stop losses are working
5. Check webhook messages arrive on time
6. Gradually increase size if profitable

---

## Troubleshooting

### Strategy Not Taking Trades

**Check:**
- Position is flat (not already in trade)
- Pyramiding set to 0 (one position at a time)
- Opposite signal exit is working (closes previous position)
- HA pattern actually formed (check dashboard)
- Backtest shows trades in history (means code works)

### Stops Too Tight (Many Small Losses)

**Solution:**
- Increase ATR Multiplier: 0.5 → 0.75 or 1.0
- Try longer ATR period: 14 → 20 or 30
- Switch to larger timeframe (15m → 1h)

### Stops Too Loose (Large Losses)

**Solution:**
- Decrease ATR Multiplier: 0.5 → 0.3 or 0.4
- Try shorter ATR period: 14 → 10 or 7
- Enable "Exit on Opposite Signal" if disabled

### Webhook Not Firing

**Check:**
- Alert created for "Order fills only"
- Message uses `{{strategy.order.alert_message}}`
- Frequency set to "Once Per Bar Close"
- Flask app is running and accessible
- Webhook URL is correct

### Exit Signal Not Closing Position

**Check:**
- "Exit on Opposite Signal" is enabled in settings
- Strategy has an open position to close
- Opposite pattern actually formed (2 HA candles)
- Check Strategy Tester trade list for exit reason

### Backtest Shows Different Results Than Real-Time

**This indicates repainting. Should NOT happen with this strategy.**

If it does:
- Verify you're using latest version (v6)
- Check "Recalculate" setting (should be "After order is filled")
- Ensure `barstate.isconfirmed` is in all signal logic
- Compare historical signals before/after page refresh

---

## Advanced Configuration

### Multiple Positions (Pyramiding)

In Strategy Properties:
- Set "Pyramiding" > 0 to allow multiple entries
- Example: Pyramiding = 2 allows 2 LONG positions
- Not recommended for this strategy (can compound losses)

### Fixed Dollar Risk Per Trade

In Strategy Properties:
- Order size: "Fixed" → enter dollar amount
- Example: $100 per trade regardless of equity
- Good for consistent risk management

### Date Range Filtering

In Strategy Properties:
- Enable "Backtest Range"
- Set start/end dates
- Useful for testing specific market conditions

### Session Filtering

Add to strategy code to only trade certain hours:
```pinescript
// Only trade during US market hours (example)
in_session = na(time(timeframe.period, "0930-1600", "America/New_York"))
long_entry_filtered = long_entry and in_session
```

---

## Quick Reference

### Strategy Summary
- **Entry**: 2 same-color HA candles (no repaint)
- **Exit 1**: Opposite 2-candle HA pattern
- **Exit 2**: ATR trailing stop (0.5x ATR)
- **Position Size**: 100% equity (configurable)
- **Commission**: 0.1% per trade

### Recommended Settings
- **Timeframe**: 15m - 1h (balance between trades and accuracy)
- **ATR Length**: 14 (standard)
- **ATR Multiplier**: 0.5 - 0.75 (adjust based on backtest)
- **Asset**: ETH/USD (or any liquid asset)

### Alert Setup
- **Type**: Order fills only
- **Message**: `{{strategy.order.alert_message}}`
- **Frequency**: Once Per Bar Close
- **Webhook**: `http://your-server:10000/webhook`

---

*Last Updated: 2026-01-23*
*Compatible with TradingView Pine Script v6*
