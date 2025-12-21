from flask import Flask, request, jsonify
from flask_cors import CORS
import hashlib, hmac, os, json
from urllib.parse import parse_qsl

app = Flask(__name__)
CORS(app)

BOT_TOKEN = os.environ.get("BOT_TOKEN")
counters = {}

def check_telegram_auth(init_data: str) -> bool:
    parsed = dict(parse_qsl(init_data, keep_blank_values=True))

    if "hash" not in parsed:
        return False

    received_hash = parsed.pop("hash")

    data_check_string = "\n".join(
        f"{k}={v}" for k, v in sorted(parsed.items())
    )

    secret_key = hashlib.sha256(BOT_TOKEN.encode()).digest()
    calculated_hash = hmac.new(
        secret_key,
        data_check_string.encode(),
        hashlib.sha256
    ).hexdigest()

    return calculated_hash == received_hash


@app.route("/click", methods=["POST", "OPTIONS"])
def click():
    if request.method == "OPTIONS":
        return ("", 204)

    data = request.get_json(silent=True)
    if not data or "initData" not in data:
        return jsonify({"ok": False, "error": "no initData"}), 400

    init_data = data["initData"]

    if not check_telegram_auth(init_data):
        return jsonify({"ok": False, "error": "invalid signature"}), 403

    parsed = dict(parse_qsl(init_data, keep_blank_values=True))
    user = json.loads(parsed["user"])
    user_id = user["id"]

    counters[user_id] = counters.get(user_id, 0) + 1

    return jsonify({
        "ok": True,
        "count": counters[user_id]
    })


@app.route("/")
def home():
    return "OK"


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 3000))
    app.run(host="0.0.0.0", port=port)
