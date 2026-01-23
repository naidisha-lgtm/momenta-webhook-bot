# TradingView Setup Guide

## Overview
This guide explains how to set up the "2 Same Color Heikin Ashi (No Repaint)" indicator in TradingView and connect it to your webhook bot.

---

## Indicator: 2 Same Color Heikin Ashi (No Repaint)

### Strategy Logic
- **LONG Signal**: Triggered when 2 consecutive Heikin Ashi candles are green (bullish)
- **SHORT Signal**: Triggered when 2 consecutive Heikin Ashi candles are red (bearish)
- Signals fire only once when the pattern first appears (not repeatedly)
- **NO REPAINTING**: Signals are confirmed only after bar closes

### Key Features

**No Repaint Guarantee:**
- Signals fire ONLY on bar close (using `barstate.isconfirmed`)
- Once a signal appears, it will never disappear or change
- Safe for automated trading - no false signals during bar formation
- Historical signals match real-time signals exactly

**Visual Display:**
- Regular candles displayed on chart (NOT Heikin Ashi candles)
- HA calculations happen in background for signal generation
- Optional: Toggle to show HA candles as overlay (disabled by default)
- Triangle markers for LONG (green up) and SHORT (red down) signals
- Background highlighting when signals occur
- Bar coloring to show when 2-candle HA pattern is active
- Info dashboard showing current HA trend and bar status

**Webhook Integration:**
- Pre-configured alert messages compatible with webhook bot
- Alerts fire only on confirmed signals (no repaint)
- JSON format: `{"signal":"LONG"}` or `{"signal":"SHORT"}`

---

## Installation Steps

### 1. Add Indicator to TradingView

1. Open TradingView and go to any chart
2. Click on "Pine Editor" at the bottom of the screen
3. Click "New" to create a new indicator
4. Copy the entire contents of `heikin_ashi_2candles.pine`
5. Paste into the Pine Editor
6. Click "Save" and give it a name (e.g., "2 Same Color HA")
7. Click "Add to Chart"

### 2. Indicator Settings

**"Show Heikin Ashi Candles" (checkbox):**
- **OFF (default)**: Chart displays regular candles, HA logic runs in background
- **ON**: Overlays semi-transparent HA candles on top of regular candles
- Recommendation: Keep OFF for cleaner chart view

**Chart Settings:**
- Works with any timeframe (5m, 15m, 1h, 4h, daily, etc.)
- Works with any asset (but webhook bot trades ETH options)
- Best on candle charts (not line/area charts)

### 3. Set Up Alerts (CRITICAL: No Repaint Settings)

The indicator is designed to avoid repainting, but you must configure alerts correctly.

#### Option A: Separate Alerts (Recommended)

**For LONG signals:**
1. Click the "Alert" button (clock icon) on the toolbar
2. Set Condition: `2 Same Color Heikin Ashi (No Repaint)` → `LONG Signal Alert`
3. Alert name: "HA 2 Green LONG"
4. **CRITICAL**: Set Frequency to "Once Per Bar Close" (NOT "Once Per Bar")
5. Message: `{"signal":"LONG"}`
6. Webhook URL: `http://your-server:10000/webhook`
7. Expiration: "Open-ended"
8. Click "Create"

**For SHORT signals:**
1. Click the "Alert" button again
2. Set Condition: `2 Same Color Heikin Ashi (No Repaint)` → `SHORT Signal Alert`
3. Alert name: "HA 2 Red SHORT"
4. **CRITICAL**: Set Frequency to "Once Per Bar Close" (NOT "Once Per Bar")
5. Message: `{"signal":"SHORT"}`
6. Webhook URL: `http://your-server:10000/webhook`
7. Expiration: "Open-ended"
8. Click "Create"

#### Option B: Combined Alert (Single Setup)

1. Click the "Alert" button
2. Set Condition: `2 Same Color Heikin Ashi (No Repaint)` → `Any Signal Alert`
3. Alert name: "HA 2 Same Color"
4. **CRITICAL**: Set Frequency to "Once Per Bar Close" (NOT "Once Per Bar")
5. Message: (pre-configured in indicator)
6. Webhook URL: `http://your-server:10000/webhook`
7. Expiration: "Open-ended"
8. Click "Create"

### 4. Alert Settings Explained

**Frequency (MOST IMPORTANT FOR NO REPAINT):**
- ✅ **"Once Per Bar Close"** - REQUIRED for no repaint. Waits for candle to fully close before firing
- ❌ "Once Per Bar" - Can fire mid-candle, may cause false signals
- ❌ "Only Once" - Fires only the first time ever, then stops

**Why "Once Per Bar Close" is Critical:**
- Ensures signal is confirmed and won't change
- Prevents mid-candle signals that disappear when bar closes
- Matches the indicator's `barstate.isconfirmed` logic
- Safe for automated trading - no false entries

**Expiration:**
- ✅ "Open-ended" - Recommended for continuous monitoring
- Or set specific date/time if testing

**Actions:**
- ✅ Webhook URL (required for automated trading)
- ✅ Notify on app (optional, for mobile notifications)
- ✅ Email (optional, for backup notifications)
- ✅ Show popup (optional, for desktop alerts)

**Webhook Configuration:**
- URL format: `http://your-server-ip:10000/webhook` or your deployed URL
- Must be accessible from TradingView servers (not localhost)
- Flask app must be running and port 10000 open

---

## Verifying No-Repaint Behavior

### How to Confirm the Indicator Doesn't Repaint

**Method 1: Watch the Dashboard**
- The info table shows "Bar Status: In Progress..." during candle formation
- It changes to "Bar Status: Closed ✓" when bar closes
- Signals only appear when status shows "Closed ✓"

**Method 2: Historical Test**
- Scroll back through historical candles
- Note where signal markers appear
- Refresh the page or reload the indicator
- Verify signals appear in EXACT same locations (no repaint!)

**Method 3: Real-Time Observation**
- Watch a candle forming that might trigger a signal
- Even if 2 HA candles are green mid-bar, signal won't fire
- Wait for candle to close completely
- Signal appears ONLY after close (not during formation)

**Method 4: Check Bar Colors**
- When "Show Heikin Ashi Candles" is OFF, regular candles show
- Bars turn light green when 2-green HA pattern is active
- Bars turn light red when 2-red HA pattern is active
- But triangle signal only appears on confirmed pattern

**What Repainting Would Look Like (This Won't Happen):**
- ❌ Signal appears mid-candle, then disappears when candle closes
- ❌ Historical signals move or disappear after page refresh
- ❌ Same chart shows different signals on different devices
- ❌ Backtest results don't match real-time signals

**What No-Repaint Looks Like (Expected Behavior):**
- ✅ Signals appear only after candle completely closes
- ✅ Historical signals stay in same location forever
- ✅ Same signals on all devices and after refreshes
- ✅ Backtest results match real-time signals exactly
- ✅ Webhook fires only once per signal, never cancels

---

## Testing the Setup

### 1. Test Locally First

Before connecting to TradingView, test your webhook endpoint:

```bash
# Start the Flask app
python app.py

# In another terminal, test the webhook
curl -X POST http://localhost:10000/webhook \
  -H "Content-Type: application/json" \
  -d '{"signal":"LONG"}'
```

You should see console output like:
```
🔥 RAW PAYLOAD: {"signal":"LONG"}
✅ PARSED JSON: {'signal': 'LONG'}
📊 ETH Spot: 3250.50
🎯 Option: ETH-31000-C
⏳ DTE: 9.8 days
💰 Premium: 125.50
🚫 NO TRADE SENT (DRY RUN)
```

### 2. Test Alert from TradingView

1. Set up one alert (LONG or SHORT) with "Once Per Bar Close" frequency
2. Wait for the pattern to appear on your chart
3. **Important**: Signal fires AFTER the 2nd candle closes, not during formation
4. Check your Flask app console for the webhook payload
5. Verify the bot logs the correct ETH option selection

### 3. Verify Signal Accuracy (Understanding HA vs Regular Candles)

**Key Point**: The indicator uses Heikin Ashi logic, but displays regular candles.

**What to Watch For:**
- Chart shows regular candles (normal OHLC bars)
- Indicator calculates HA candles in background
- 2 consecutive green **HA** candles → LONG signal
- 2 consecutive red **HA** candles → SHORT signal
- Signal appears on regular candle chart AFTER 2nd HA candle closes

**Tip**: Enable "Show Heikin Ashi Candles" setting temporarily to see:
- Semi-transparent HA candles overlayed on regular candles
- Helps understand when HA candles are green/red
- This is for learning only - disable for cleaner chart

**Testing Checklist:**
- ✅ Signal appears only after bar closes (not mid-bar)
- ✅ LONG signal when 2 green HA candles form
- ✅ SHORT signal when 2 red HA candles form
- ✅ No signal if HA candles alternate colors
- ✅ Bar color highlights when pattern is active
- ✅ Dashboard shows "Closed ✓" when signal fires

---

## Troubleshooting

### Alert Not Firing

**Check:**
- Alert is active (not paused)
- Alert hasn't expired
- Pattern actually occurred (2 same-color **HA** candles, not regular candles)
- Alert frequency set to "Once Per Bar Close" (not "Once Per Bar")
- Candle has fully closed (wait for next candle to begin)

### Signal Appears Then Disappears (Repainting)

**This should NEVER happen with this indicator. If it does:**
- ❌ Alert frequency set to "Once Per Bar" instead of "Once Per Bar Close"
- ❌ Using older version of indicator (update to v6)
- ❌ Chart not refreshed - try reloading indicator
- ✅ Verify indicator name includes "(No Repaint)"
- ✅ Check dashboard shows "Bar Status: Closed ✓" when signal fires

### Webhook Not Received

**Check:**
- Flask app is running
- Port 10000 is open and accessible
- Webhook URL is correct (include http:// and port)
- Firewall isn't blocking incoming requests
- If deployed, use public IP/domain, not localhost

### Wrong Signal Received

**Check:**
- Alert message format: `{"signal":"LONG"}` or `{"signal":"SHORT"}`
- Message has correct quotes (double quotes, not single)
- No extra text in the message field
- Webhook endpoint is `/webhook` not `/`

### Bot Not Selecting Options

**Check bot logs for:**
- `❌ INVALID SIGNAL` - message format is wrong
- `❌ NO OPTION FOUND` - no suitable options available
- Delta Exchange API errors - network or API issues

---

## Chart Recommendations

### Timeframes
- **5m - 15m**: Good for active trading, frequent signals
- **1h - 4h**: Medium-term signals, fewer false positives
- **Daily**: Long-term trend following

### Assets
The indicator works on any asset, but your webhook bot is configured for ETH:
- Recommended: ETH/USD, ETH/USDT charts
- The bot will always trade ETH options regardless of the chart asset

### Combining with Other Indicators
Consider adding:
- Volume indicators (confirm strength)
- RSI (avoid overbought/oversold)
- Moving averages (trend confirmation)
- Support/Resistance levels

---

## Webhook Message Format

The indicator sends JSON in this format:

```json
{
  "signal": "LONG"
}
```

or

```json
{
  "signal": "SHORT"
}
```

Your webhook bot (`app.py`) expects:
- Content-Type: `application/json`
- POST method
- A `signal` field with value "LONG" or "SHORT"

---

## Advanced Customization

### Modify Signal Logic

To change the pattern detection, edit these lines in the Pine script:

```pinescript
// Change to 3 consecutive candles
two_green = current_bullish and prev_bullish and ha_close[2] > ha_open[2]
two_red = current_bearish and prev_bearish and ha_close[2] < ha_open[2]
```

### Add Filters

Add conditions to reduce false signals:

```pinescript
// Example: Only signal if candle size is significant
candle_size = math.abs(ha_close - ha_open)
avg_size = ta.sma(candle_size, 20)
long_signal = two_green and not two_green[1] and candle_size > avg_size * 0.5
```

### Change Alert Messages

Modify the alertcondition messages:

```pinescript
alertcondition(long_signal,
               title="LONG Signal Alert",
               message='{"signal":"LONG","timeframe":"{{interval}}","price":"{{close}}"}')
```

---

## Production Checklist

Before going live:

- [ ] Flask app is deployed on a reliable server
- [ ] Webhook URL is using HTTPS (recommended)
- [ ] Alerts are tested and working
- [ ] Bot correctly selects ETH options
- [ ] Remove DRY RUN mode (only if ready to trade)
- [ ] Implement position sizing logic
- [ ] Add risk management checks
- [ ] Set up monitoring/logging
- [ ] Configure Delta Exchange API authentication
- [ ] Test with small positions first

---

## Example Workflow

1. **Market opens** → 2 green Heikin Ashi candles form
2. **TradingView** → Detects pattern, sends webhook
3. **Webhook bot** → Receives `{"signal":"LONG"}`
4. **Bot queries** → Gets ETH spot price and options list
5. **Bot selects** → ATM call option ~10 DTE
6. **Bot logs** → Prints selection details (DRY RUN)
7. **Future** → Execute trade on Delta Exchange (when ready)

---

## Support

For issues:
- Check Flask app console logs
- Verify TradingView alert history
- Test webhook with curl
- Review `CLAUDE.md` for bot documentation

---

*Last Updated: 2026-01-23*
