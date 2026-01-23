# TradingView Setup Guide

## Overview
This guide explains how to set up the "2 Same Color Heikin Ashi" indicator in TradingView and connect it to your webhook bot.

---

## Indicator: 2 Same Color Heikin Ashi

### Strategy Logic
- **LONG Signal**: Triggered when 2 consecutive Heikin Ashi candles are green (bullish)
- **SHORT Signal**: Triggered when 2 consecutive Heikin Ashi candles are red (bearish)
- Signals fire only once when the pattern first appears (not repeatedly)

### Features
- Visual Heikin Ashi candles plotted on chart
- Triangle markers for LONG (green up) and SHORT (red down) signals
- Background highlighting when signals occur
- Info dashboard showing current state
- Pre-configured alert messages compatible with webhook bot

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

### 2. Indicator Settings (Optional)

The indicator works out of the box, but you can customize:
- Candle colors (green/red by default)
- Signal marker size and style
- Background highlight opacity
- Dashboard position (top-right by default)

### 3. Set Up Alerts

#### Option A: Separate Alerts (Recommended for Testing)

**For LONG signals:**
1. Click the "Alert" button (clock icon) on the toolbar
2. Set Condition: `2 Same Color Heikin Ashi` → `LONG Signal Alert`
3. Alert name: "HA 2 Green LONG"
4. Message: `{"signal":"LONG"}`
5. Webhook URL: `http://your-server:10000/webhook`
6. Click "Create"

**For SHORT signals:**
1. Click the "Alert" button again
2. Set Condition: `2 Same Color Heikin Ashi` → `SHORT Signal Alert`
3. Alert name: "HA 2 Red SHORT"
4. Message: `{"signal":"SHORT"}`
5. Webhook URL: `http://your-server:10000/webhook`
6. Click "Create"

#### Option B: Combined Alert (Single Setup)

1. Click the "Alert" button
2. Set Condition: `2 Same Color Heikin Ashi` → `Any Signal Alert`
3. Alert name: "HA 2 Same Color"
4. Message: (use the pre-configured message in the indicator)
5. Webhook URL: `http://your-server:10000/webhook`
6. Click "Create"

### 4. Alert Settings

Configure these settings for each alert:

**Frequency:**
- "Once Per Bar Close" (recommended) - waits for candle to close
- "Only Once" - fires only the first time
- "Once Per Bar" - can fire multiple times per candle

**Expiration:**
- Set to "Open-ended" for continuous monitoring
- Or set specific date/time if testing

**Actions:**
- ✅ Webhook URL (required)
- ✅ Notify on app (optional)
- ✅ Email (optional)

**Webhook Configuration:**
- URL: `http://your-server-ip:10000/webhook` or your deployed URL
- Make sure your Flask app is running and accessible

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

1. Set up one alert (LONG or SHORT)
2. Wait for the pattern to appear on your chart
3. Check your Flask app console for the webhook payload
4. Verify the bot logs the correct ETH option selection

### 3. Verify Signal Accuracy

- Watch for 2 consecutive green candles → should trigger LONG
- Watch for 2 consecutive red candles → should trigger SHORT
- No signal should fire if candles alternate colors

---

## Troubleshooting

### Alert Not Firing

**Check:**
- Alert is active (not paused)
- Alert hasn't expired
- Pattern actually occurred (2 same-color candles)
- Alert frequency settings allow it to fire

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
