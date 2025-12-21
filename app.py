from flask import Flask, request, jsonify
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

counter = 0

@app.route("/click", methods=["POST"])
def click():
    global counter
    counter += 1
    return jsonify({
        "ok": True,
        "count": counter
    })

@app.route("/")
def home():
    return "Server is running"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 3000))
    app.run(host="0.0.0.0", port=port)
