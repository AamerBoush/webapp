from flask import Flask, request, jsonify
import hashlib, hmac, os, json
from urllib.parse import parse_qsl

app = Flask(__name__)

BOT_TOKEN = os.environ.get("BOT_TOKEN")
counters = {}

@app.route("/")
def home():
    return "OK"

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


# 🔥 نوقف Flask من أي parsing تلقائي
@app.route("/click", methods=["POST"], provide_automatic_options=False)
def click():
    # نقرأ RAW BODY فقط
    init_data = request.get_data(as_text=True)

    if not init_data:
        return jsonify({"ok": False, "error": "no data"}), 400

    if not verify_telegram(init_data):
        return jsonify({"ok": False, "error": "invalid signature"}), 403

    data = dict(parse_qsl(init_data))
    user = json.loads(data["user"])
    user_id = user["id"]

    counters[user_id] = counters.get(user_id, 0) + 1

    return jsonify({
        "ok": True,
        "count": counters[user_id]
    })
