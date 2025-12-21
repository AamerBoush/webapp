from flask import Flask, request, jsonify
from flask_cors import CORS
import hashlib, hmac, os, json
from urllib.parse import parse_qsl

app = Flask(__name__)
CORS(app)

BOT_TOKEN = os.environ.get("8221519604:AAGQMTlvAJPu0wVOs47XO_IrN_F4rKgn5WU")
counters = {}

@app.route("/")
def home():
    return "Server is running ✅"

def verify_telegram(init_data):
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
    body = request.get_json()

    if not body or "initData" not in body:
        return jsonify({"ok": False, "error": "no initData"}), 400

    if not verify_telegram(body["initData"]):
        return jsonify({"ok": False, "error": "invalid signature"}), 403

    data = dict(parse_qsl(body["initData"]))
    user = json.loads(data["user"])
    user_id = user["id"]

    counters[user_id] = counters.get(user_id, 0) + 1

    return jsonify({"ok": True, "count": counters[user_id]})
