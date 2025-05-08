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
    while not bot.is_closed():
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=5)) as s:
                url = os.getenv("KOYEB_APP_URL", "").rstrip("/") + "/health"
                async with s.get(url) as res:
                    logging.info(f"🔁 Self Ping 응답: {res.status}")
        except Exception as e:
            logging.warning(f"⚠️ Self Ping 실패: {e}")
        await asyncio.sleep(180)  # 3분마다 ping

async def main():
    logging.basicConfig(level=logging.INFO)
    asyncio.create_task(start_web_server())
    asyncio.create_task(ping_self())
    await bot.start(DISCORD_TOKEN)

if __name__ == "__main__":
    asyncio.run(main())
