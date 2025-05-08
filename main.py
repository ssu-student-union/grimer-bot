import os
import logging
import asyncio
import aiohttp
from aiohttp import web
from discord_bot.bot import bot  

from dotenv import load_dotenv
load_dotenv()

KOYEB_URL = os.getenv("KOYEB_APP_URL")
DISCORD_TOKEN = os.getenv("DISCORD_BOT_TOKEN")

async def health_check(request):
    return web.Response(text="OK", status=200)

async def start_web_server():
    app = web.Application()
    app.router.add_get("/health", health_check)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", 8000)
    await site.start()

async def ping_self():
    await bot.wait_until_ready()
    if not KOYEB_URL:
        logging.warning("❌ KOYEB_APP_URL 환경변수가 비어있습니다. Self Ping이 작동하지 않습니다.")
        return
    while not bot.is_closed():
        try:
            async with aiohttp.ClientSession() as s:
                url = f"{KOYEB_URL.rstrip('/')}/health"
                logging.info(f"🔄 Self-ping 요청 중... → {url}")
                async with s.get(url) as response:
                    logging.info(f"✅ Self-ping 응답 상태: {response.status}")
        except Exception as e:
            logging.warning(f"⚠️ Self-ping 실패: {e}")
        await asyncio.sleep(180)

async def main():
    logging.basicConfig(level=logging.INFO)
    asyncio.create_task(start_web_server())
    asyncio.create_task(ping_self())
    await bot.start(DISCORD_TOKEN)

if __name__ == "__main__":
    asyncio.run(main())
