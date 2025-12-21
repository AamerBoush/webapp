from flask import Flask, request, jsonify
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

# عداد لكل مستخدم
counters = {}

@app.route("/click", methods=["POST"])
def click():
    data = request.get_json(silent=True)

    if not data or "user_id" not in data:
        return jsonify({"ok": False, "error": "no user id"}), 400

    user_id = str(data["user_id"])

    counters[user_id] = counters.get(user_id, 0) + 1

    return jsonify({
        "ok": True,
        "user_id": user_id,
        "count": counters[user_id]
    })

@app.route("/")
def home():
    return "Server running"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 3000))
    app.run(host="0.0.0.0", port=port)
