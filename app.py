from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json(force=True)
    print("📥 RECEIVED ALERT:", data, flush=True)
    return jsonify({"status": "ok"}), 200

@app.route("/", methods=["GET"])
def health():
    return "Momenta webhook bot is running", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)

