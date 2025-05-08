import os
import logging
import asyncio
import aiohttp
from aiohttp import web
from dotenv import load_dotenv
from discord_bot.bot import bot  

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
        return
    while not bot.is_closed():
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=3)) as s:
                url = KOYEB_URL.rstrip("/") + "/health"
                async with s.get(url):
                    pass
        except:
            pass
        await asyncio.sleep(60)

async def main():
    logging.basicConfig(level=logging.INFO)
    asyncio.create_task(start_web_server())
    asyncio.create_task(ping_self())
    await bot.start(DISCORD_TOKEN)

if __name__ == "__main__":
    asyncio.run(main())
