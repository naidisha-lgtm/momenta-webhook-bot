# CLAUDE.md - AI Assistant Guide

## Project Overview

**momenta-webhook-bot** is a Flask-based trading webhook bot that receives signals from TradingView and interacts with Delta Exchange API to analyze ETH options trading opportunities.

### Key Characteristics
- **Language**: Python 3.x
- **Framework**: Flask (lightweight web server)
- **Purpose**: Receive trading signals and select appropriate ETH options on Delta Exchange
- **Status**: Currently in DRY RUN mode (no actual trades executed)
- **Architecture**: Single-file application (app.py)

---

## Repository Structure

```
momenta-webhook-bot/
├── app.py              # Main application file (Flask server + all logic)
├── requirements.txt    # Python dependencies
└── README.md          # Basic project description
```

### File Descriptions

#### app.py (119 lines)
The entire application logic in a single file:

**Key Components:**
1. **Delta Data Helpers** (lines 11-61)
   - `get_eth_spot_price()`: Fetches current ETH/USD spot price
   - `get_eth_options()`: Retrieves all ETH options from Delta Exchange
   - `pick_atm_option(options, spot, side)`: Selects ATM option ~10 DTE
   - `get_option_price(symbol)`: Gets current option premium

2. **Webhook Endpoint** (lines 67-102)
   - `POST /webhook`: Receives TradingView signals
   - Validates JSON payload with signal field ("LONG" or "SHORT")
   - Queries Delta Exchange for ETH spot and options data
   - Selects appropriate ATM call (LONG) or put (SHORT) option
   - Logs selection details (DRY RUN - no execution)

3. **Health Check** (lines 109-111)
   - `GET /`: Basic health check endpoint

4. **Entry Point** (lines 118-119)
   - Runs Flask on 0.0.0.0:10000

#### requirements.txt
Minimal dependencies:
- `flask`: Web framework
- `requests`: HTTP client for API calls

---

## Development Workflows

### Making Changes

1. **Always read app.py first** before making modifications
2. **Test webhooks locally** by sending POST requests to /webhook
3. **Verify Delta Exchange API compatibility** when modifying API calls
4. **Maintain dry run safety** - don't remove execution guards without explicit permission

### Common Tasks

#### Adding New Features
- Keep logic in app.py unless complexity demands refactoring
- Follow existing code structure (helper functions, then routes)
- Add console logging with emoji prefixes for visibility (🔥, ✅, ❌, etc.)

#### Modifying Option Selection Logic
- Located in `pick_atm_option()` function (lines 35-54)
- Current logic: ~10 DTE, closest to ATM strike
- Parameters: options list, spot price, side (LONG/SHORT)

#### API Integration Changes
- Base URL: `https://api.delta.exchange`
- Key endpoints used:
  - `/v2/tickers`: Spot prices
  - `/v2/tickers/{symbol}`: Option prices
  - `/v2/products`: All products including options

### Testing Locally

```bash
# Install dependencies
pip install -r requirements.txt

# Run the server
python app.py

# Test webhook (different terminal)
curl -X POST http://localhost:10000/webhook \
  -H "Content-Type: application/json" \
  -d '{"signal":"LONG"}'
```

### Deployment Notes
- Application runs on port 10000
- Listens on all interfaces (0.0.0.0)
- No environment variables currently used
- No database or persistent storage
- Stateless - each webhook processed independently

---

## Code Conventions

### Style Guidelines
1. **Functions**: Snake_case naming
2. **Constants**: UPPER_CASE (e.g., DELTA_BASE)
3. **Logging**: Use print() with flush=True and emoji prefixes
4. **Error Handling**: Try/except with graceful fallbacks, always return 200 OK
5. **Comments**: Section headers with `===` borders

### Emoji Logging Convention
- 🔥 Raw input/payload received
- ✅ Successful parsing/validation
- ⚠️ Warning (non-critical issue)
- ❌ Error/invalid data
- 🧠 Logic decision
- 📊 Data/metrics
- 🎯 Selection/target
- ⏳ Time-related
- 💰 Price/financial
- 🚫 Blocked/prevented action

### Safety Practices
1. **Never execute real trades without explicit removal of DRY RUN mode**
2. **Always return 200 OK** from webhook endpoint (TradingView expects this)
3. **Validate signal values** before processing (must be "LONG" or "SHORT")
4. **Handle JSON parse errors gracefully** - don't crash on malformed payloads
5. **Log all decisions** for debugging and audit trail

---

## Option Selection Algorithm

### Current Logic (lines 35-54)

**For LONG signals:**
- Select call options (`contract_type == "call_option"`)

**For SHORT signals:**
- Select put options (`contract_type == "put_option"`)

**Selection criteria:**
1. Filter by option type (call/put)
2. Calculate days to expiry (DTE)
3. Sort by closest to 10 DTE
4. Take top 20 by expiry
5. From those 20, sort by strike price closest to spot (ATM)
6. Return the closest ATM option

### Key Formulas
```python
days_to_expiry = abs((settlement_time_ms / 1000) - now_timestamp) / 86400
```

---

## API Dependencies

### Delta Exchange API
- **Documentation**: https://docs.delta.exchange
- **Base URL**: https://api.delta.exchange
- **Authentication**: Not required for public market data endpoints
- **Rate Limits**: Unknown (not currently handled)

### Endpoints Used
| Endpoint | Purpose | Response Field |
|----------|---------|----------------|
| `/v2/tickers` | Get all tickers including ETH spot | `result[].symbol`, `result[].last_price` |
| `/v2/tickers/{symbol}` | Get specific option price | `result.last_price` |
| `/v2/products` | Get all products | `result[].contract_type`, `result[].underlying_asset` |

### Expected Data Structures
```python
# Ticker object
{
  "symbol": "ETHUSD",
  "last_price": "3250.50"
}

# Product/Option object
{
  "symbol": "ETH-30000-C",
  "contract_type": "call_option",
  "underlying_asset": "ETH",
  "strike_price": "30000",
  "settlement_time": 1738886400000  # Unix timestamp in milliseconds
}
```

---

## Webhook Integration

### TradingView Configuration
**Expected Payload:**
```json
{
  "signal": "LONG"  // or "SHORT"
}
```

**Alert Setup in TradingView:**
- URL: `http://your-server:10000/webhook`
- Method: POST
- Content-Type: application/json
- Body: `{"signal":"{{strategy.order.action}}"}`

### Webhook Behavior
1. Accept any payload (always return 200 OK)
2. Attempt JSON parsing, skip if invalid
3. Validate signal field presence and value
4. Query Delta Exchange APIs
5. Log selection decision
6. **Do not execute trade** (DRY RUN)

---

## Important Constraints

### What NOT to Do
1. ❌ Don't remove DRY RUN guards without explicit permission
2. ❌ Don't add authentication/API keys for Delta Exchange without confirming account setup
3. ❌ Don't change webhook response status (must always be 200)
4. ❌ Don't add complex error responses (TradingView needs simple 200 OK)
5. ❌ Don't create separate config files without discussing structure first
6. ❌ Don't add database dependencies without explicit requirements

### What TO Do
1. ✅ Keep the application simple and readable
2. ✅ Add logging for debugging
3. ✅ Validate inputs defensively
4. ✅ Handle API failures gracefully
5. ✅ Maintain single-file structure unless refactoring is explicitly requested
6. ✅ Test changes with curl or similar tools
7. ✅ Document logic changes in commit messages

---

## Git Workflow

### Branch Naming
- Feature branches: `claude/claude-md-*` (auto-generated)
- Always develop on designated Claude branches
- Never push to main without explicit permission

### Commit Guidelines
1. Use clear, descriptive commit messages
2. Focus on "why" rather than "what"
3. Keep commits atomic (one logical change per commit)
4. Include session URL in commit body

### Push Protocol
```bash
# Always use -u flag for new branches
git push -u origin <branch-name>

# Branch must start with 'claude/' and match session ID
# Retry on network errors: 2s, 4s, 8s, 16s backoff
```

---

## Troubleshooting Guide

### Common Issues

**Webhook not receiving data:**
- Check Flask is running on 0.0.0.0:10000
- Verify TradingView webhook URL is correct
- Check firewall/port forwarding

**No ETH spot price:**
- Delta Exchange API may be down
- ETHUSD ticker may have different symbol
- Check `/v2/tickers` response structure

**No options found:**
- May be outside trading hours
- Underlying asset filter may need adjustment
- Check if Delta Exchange lists ETH options

**Option selection fails:**
- Not enough options available near 10 DTE
- No options available at ATM strikes
- Check `pick_atm_option()` logic and logging

---

## Future Enhancement Areas

### Potential Improvements (not yet implemented)
- Environment variables for configuration
- Authentication for Delta Exchange trading API
- Database for trade history
- Position sizing logic
- Risk management checks
- Multiple underlying assets (not just ETH)
- Configurable DTE target
- Retry logic for API failures
- Rate limiting for webhook endpoint
- Unit tests
- Docker containerization

**Note:** Only implement these if explicitly requested. Keep the application simple by default.

---

## Quick Reference

### Running the Application
```bash
python app.py  # Starts on http://0.0.0.0:10000
```

### Testing Webhook
```bash
# LONG signal
curl -X POST http://localhost:10000/webhook \
  -H "Content-Type: application/json" \
  -d '{"signal":"LONG"}'

# SHORT signal
curl -X POST http://localhost:10000/webhook \
  -H "Content-Type: application/json" \
  -d '{"signal":"SHORT"}'
```

### Health Check
```bash
curl http://localhost:10000/  # Should return "Momenta bot running"
```

---

## Contact & Context

- **Repository**: naidisha-lgtm/momenta-webhook-bot
- **Current Branch**: claude/claude-md-mkr4vlza7e4zc2l2-QVTKh
- **Platform**: Linux 4.4.0
- **Python Version**: Python 3.x (specify version with `python --version`)

---

*Last Updated: 2026-01-23*
*This document is maintained for AI assistants working on this codebase*
