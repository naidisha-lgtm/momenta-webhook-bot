from flask import Flask, request, jsonify
import requests
from datetime import datetime

app = Flask(__name__)

DELTA_BASE = "https://api.delta.exchange"

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
        if p["contract_type"] == "call_option" or p["contract_type"] == "put_option":
            if p["underlying_asset"] == "ETH":
                options.append(p)
    return options

def pick_atm_option(options, spot, side):
    # side = "LONG" → CALL, "SHORT" → PUT
    option_type = "call_option" if side == "LONG" else "put_option"

    # keep only correct type
    filtered = [o for o in options if o["contract_type"] == option_type]

    # sort by expiry proximity (≈ 10 days)
    today = datetime.utcnow().timestamp()
    for o in filtered:
        o["days_to_expiry"] = abs(
            (o["settlement_time"] / 1000) - today
        ) / 86400

    filtered.sort(key=lambda x: abs(x["days_to_expiry"] - 10))

    # take nearest expiry candidates
    nearest_expiry = filtered[:20]

    # pick ATM strike
    nearest_expiry.sort(key=lambda x: abs(float(x["strike_price"]) - spot))

    return nearest_expiry[0] if nearest_expiry else None

def get_option_price(symbol):
    url = f"{DELTA_BASE}/v2/tickers/{symbol}"
    r = requests.get(url).json()
    return float(r["result"]["last_price"])

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json(force=True)
    print("📥 SIGNAL RECEIVED:", data, flush=True)

    side = data.get("signal")
    if side not in ["LONG", "SHORT"]:
        return jsonify({"error": "invalid signal"}), 400

    spot = get_eth_spot_price()
    options = get_eth_options()
    option = pick_atm_option(options, spot, side)

    if not option:
        print("❌ No option found", flush=True)
        return jsonify({"status": "no option"}), 200

    premium = get_option_price(option["symbol"])

    print("🧠 DRY RUN — REAL PRICING", flush=True)
    print(f"📊 ETH Spot: {spot}", flush=True)
    print(f"🎯 Option: {option['symbol']}", flush=True)
    print(f"⏳ DTE: {round(option['days_to_expiry'],1)} days", flush=True)
    print(f"💰 Premium: {premium}", flush=True)
    print("🚫 NO TRADE SENT (DRY RUN)", flush=True)

    return jsonify({"status": "ok"}), 200

@app.route("/", methods=["GET"])
def health():
    return "Momenta bot running", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
