from flask import Flask, request

import os

app = Flask(__name__)

@app.route("/replit-webhook", methods=["POST"])
def restart_bot():
    os.system("kill 1")  # This restarts the Replit environment
    return "Bot restarting...", 200

app.run(host="0.0.0.0", port=8080)
