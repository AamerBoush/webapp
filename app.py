from flask import Flask, request, jsonify
from flask_cors import CORS
import hashlib, hmac, os, json
from urllib.parse import parse_qsl

app = Flask(__name__)

CORS(
    app,
    resources={r"/*": {"origins": "*"}},
    allow_headers=["Content-Type"],
    methods=["POST", "OPTIONS"]
)

BOT_TOKEN = os.environ.get("BOT_TOKEN")
counters = {}

def verify_telegram(init_data: str) -> bool:
    data = dict(parse_qsl(init_data))
    received_hash = data.pop("hash", None)
    if not received_hash:
        return False

    data_check_string = "\n".join(
        f"{k}={v}" for k, v in sorted(data.items())
    )

    secret_key = hashlib.sha256(BOT_TOKEN.encode()).digest()
    computed_hash = hmac.new(
        secret_key,
        data_check_string.encode(),
        hashlib.sha256
    ).hexdigest()

    return computed_hash == received_hash


@app.route("/click", methods=["POST", "OPTIONS"])
def click():
    print(init_data)

    if request.method == "OPTIONS":
        return ("", 204)

    data = request.get_json(silent=True)
    if not data or "initData" not in data:
        return jsonify({"ok": False}), 400

    init_data = data["initData"]

    if not verify_telegram(init_data):
        return jsonify({"ok": False}), 403

    parsed = dict(parse_qsl(init_data))
    user = json.loads(parsed["user"])
    user_id = user["id"]

    counters[user_id] = counters.get(user_id, 0) + 1

    return jsonify({"ok": True, "count": counters[user_id]})


@app.route("/")
def home():
    return "OK"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 3000))
    app.run(host="0.0.0.0", port=port)

