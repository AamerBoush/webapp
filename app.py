from flask import Flask, request, jsonify
from flask_cors import CORS
import hashlib, hmac, os, json
from urllib.parse import parse_qsl

app = Flask(__name__)
CORS(app)

BOT_TOKEN = os.environ.get("BOT_TOKEN")
counters = {}

def verify_telegram(init_data: str) -> bool:
    data = dict(parse_qsl(init_data, keep_blank_values=True))
    received_hash = data.pop("hash", None)
    if not received_hash:
        return False

    data_check_string = "\n".join(
        f"{k}={v}" for k, v in sorted(data.items())
    )

    secret_key = hashlib.sha256(BOT_TOKEN.encode()).digest()
    calculated_hash = hmac.new(
        secret_key,
        data_check_string.encode(),
        hashlib.sha256
    ).hexdigest()

    return calculated_hash == received_hash


@app.route("/click", methods=["POST"])
def click():
    data = request.get_json(silent=True)
    init_data = data.get("initData")

    if not verify_telegram(init_data):
        return jsonify({"ok": False}), 403

    parsed = dict(parse_qsl(init_data, keep_blank_values=True))
    user = json.loads(parsed["user"])
    user_id = str(user["id"])

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
