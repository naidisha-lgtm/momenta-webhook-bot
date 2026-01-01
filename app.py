from flask import Flask, request, jsonify
import requests
import json
from datetime import datetime

app = Flask(__name__)

DELTA_BASE = "https://api.delta.exchange"


# =========================
# DELTA DATA HELPERS
# =========================

def get_eth_spot_price():
    url = f"{DELTA_BASE}/v2/tickers"
    r = requests.get(url).json()
    for item in r["result"]:
        if item["symbol"] == "ETHUSD":
            return float(item["last_price"])
    return None


def get_eth_options():
    url = f"{DELTA_BASE}/v2/products"
    r = requests.get(url).json()
    options = []
    for p in r["result"]:
        if p["contract_type"] in ["call_option", "put_option"]:
            if p["underlying_asset"] == "ETH":
                options.append(p)
    return options


def pick_atm_option(options, spot, side):
    option_type = "call_option" if side == "LONG" else "put_option"

    filtered = [o for o in options if o["contract_type"] == option_type]
    if not filtered:
        return None

    now = datetime.utcnow().timestamp()

    for o in filtered:
        o["days_to_expiry"] = abs((o["settlement_time"] / 1000) - now) / 86400

    # closest to ~10 DTE
    filtered.sort(key=lambda x: abs(x["days_to_expiry"] - 10))
    nearest_expiry = filtered[:20]

    # ATM strike
    nearest_expiry.sort(key=lambda x: abs(float(x["strike_price"]) - spot))

    return nearest_expiry[0]


def get_option_price(symbol):
    url = f"{DELTA_BASE}/v2/tickers/{symbol}"
    r = requests.get(url).json()
    return float(r["result"]["last_price"])


# =========================
# WEBHOOK (FIXED & SAFE)
# =========================

@app.route("/webhook", methods=["POST"])
def webhook():
    raw = request.get_data(as_text=True)
    print("🔥 RAW PAYLOAD:", raw, flush=True)

    # Attempt JSON parse — NEVER FAIL
    try:
        data = json.loads(raw)
        print("✅ PARSED JSON:", data, flush=True)
    except Exception:
        print("⚠️ NON-JSON PAYLOAD RECEIVED", flush=True)
        return "OK", 200

    side = data.get("signal")
    if side not in ["LONG", "SHORT"]:
        print("❌ INVALID SIGNAL", flush=True)
        return "OK", 200

    spot = get_eth_spot_price()
    options = get_eth_options()
    option = pick_atm_option(options, spot, side)

    if not option:
        print("❌ NO OPTION FOUND", flush=True)
        return "OK", 200

    premium = get_option_price(option["symbol"])

    print("🧠 DRY RUN — REAL DELTA PRICING", flush=True)
    print(f"📊 ETH Spot: {spot}", flush=True)
    print(f"🎯 Option: {option['symbol']}", flush=True)
    print(f"⏳ DTE: {round(option['days_to_expiry'], 1)} days", flush=True)
    print(f"💰 Premium: {premium}", flush=True)
    print("🚫 NO TRADE SENT (DRY RUN)", flush=True)

    return "OK", 200


# =========================
# HEALTH CHECK
# =========================

@app.route("/", methods=["GET"])
def health():
    return "Momenta bot running", 200


# =========================
# ENTRY POINT
# =========================

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
