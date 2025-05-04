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
    port = int(os.environ.get("PORT", 8000)) 
    app.run(host="0.0.0.0", port=port)

def self_ping():
    if not koyeb_url:
        logging.warning("❌ KOYEB_APP_URL 환경변수가 비어있습니다. Self Ping이 작동하지 않습니다.")
        return
    time.sleep(10)  # Flask 서버가 먼저 올라올 수 있게 약간 대기
    while True:
        try:
            url = f"{koyeb_url.rstrip('/')}/health"
            logging.info(f"🔄 Self-ping 요청 중... → {url}")
            response = requests.get(url, timeout=10)
            logging.info(f"✅ Self-ping 응답 상태: {response.status_code}")
        except Exception as e:
            logging.warning(f"⚠️ Self-ping 실패: {e}")
        time.sleep(300)

if __name__ == "__main__":
    threading.Thread(target=run_flask, daemon=True).start()
    threading.Thread(target=self_ping, daemon=True).start()
    run_bot(token)
