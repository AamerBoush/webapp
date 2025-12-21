from flask import Flask, request, jsonify
import hashlib, hmac, os, json
from urllib.parse import parse_qsl

app = Flask(__name__)

BOT_TOKEN = os.environ.get("BOT_TOKEN")
counters = {}

@app.route("/")
def home():
    return "OK"

# 🔐 تحقق Telegram
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


# ✅ نسمح بكل شيء: POST + OPTIONS
@app.route("/click", methods=["POST", "OPTIONS"])
def click():

    # 🔥 إذا OPTIONS (preflight) نرد مباشرة
    if request.method == "OPTIONS":
        return ("", 204)

    # 🔥 نقرأ initData من أي مكان ممكن
    init_data = (
        request.form.get("initData")
        or (request.json.get("initData") if request.is_json else None)
        or request.data.decode(errors="ignore")
    )

    if not init_data:
        return jsonify({"ok": False, "error": "no initData"}), 400

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
