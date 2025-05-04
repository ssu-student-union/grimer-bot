# main.py
import os
import logging
import threading
import time
import requests
from flask import Flask
from dotenv import load_dotenv
from discord_bot.bot import run_bot

load_dotenv()
logging.basicConfig(level=logging.INFO)

token = os.getenv("DISCORD_BOT_TOKEN")
koyeb_url = os.getenv("KOYEB_APP_URL")

app = Flask(__name__)

@app.route("/")
def home():
    return "✅ Grimer bot is alive with Flask + Discord + Instagram"

@app.route("/health")
def health():
    return "OK", 200

def run_flask():
    app.run(host="0.0.0.0", port=10000)

def self_ping():
    if not koyeb_url:
        logging.warning("❌ KOYEB_APP_URL 환경변수가 비어있습니다. Self Ping이 작동하지 않습니다.")
        return
    while True:
        try:
            logging.info("🔄 Self-ping 요청 중...")
            requests.get(koyeb_url, timeout=10)
        except Exception as e:
            logging.warning(f"⚠️ Self-ping 실패: {e}")
        time.sleep(300)

if __name__ == "__main__":
    threading.Thread(target=run_flask, daemon=True).start()
    threading.Thread(target=self_ping, daemon=True).start()
    run_bot(token)
