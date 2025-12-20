from flask import Flask, request, jsonify
import hashlib
import hmac
from urllib.parse import parse_qsl
import json
import os
app = Flask(__name__)

BOT_TOKEN = "8221519604:AAGQMTlvAJPu0wVOs47XO_IrN_F4rKgn5WU"

# تخزين مؤقت (بدل DB)
counters = {}

def verify_telegram(init_data: str) -> bool:
    data = dict(parse_qsl(init_data))
    received_hash = data.pop("hash", None)

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


@app.route("/click", methods=["POST"])
def click():
    init_data = request.json.get("initData")

    if not verify_telegram(init_data):
        return jsonify({"ok": False}), 403

    data = dict(parse_qsl(init_data))
    user = json.loads(data["user"])
    user_id = user["id"]

    counters[user_id] = counters.get(user_id, 0) + 1

    return jsonify({
        "ok": True,
        "count": counters[user_id]
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 3000)))
