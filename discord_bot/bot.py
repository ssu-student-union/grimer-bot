import os
import logging
import discord
from discord.ext import commands, tasks
from utils import insta_checker
from dotenv import load_dotenv

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

TARGET_CHANNEL_ID = int(os.getenv("TARGET_CHANNEL_ID", 0))
COUNSIL_URL = os.getenv("COUNSIL_URL", "")

@bot.event
async def on_ready():
    monitor_instagram.start()

@tasks.loop(minutes=5)
async def monitor_instagram():
    new_post = await bot.loop.run_in_executor(None, insta_checker.check_new_post)
    if new_post and not new_post.get("error"):
        await send_post_message(await get_target_channel(), new_post)

@bot.command(name="insta_check")
async def insta_check(ctx):
    new_post = await bot.loop.run_in_executor(None, insta_checker.check_new_post)
    if new_post and not new_post.get("error"):
        await send_post_message(ctx.channel, new_post)
    else:
        await ctx.send("🛌 새 게시물이 없습니다.")

async def get_target_channel():
    if TARGET_CHANNEL_ID:
        return bot.get_channel(TARGET_CHANNEL_ID)
    if bot.guilds:
        return bot.guilds[0].text_channels[0]
    return None

async def send_post_message(destination, post):
    if not destination:
        return
    title = post.get("title", "제목 없음")
    content = post.get("content", "")
    images = post.get("images", [])
    post_id = post.get("post_id")

    if content.startswith(title):
        content = content[len(title):].lstrip("\n")

    text = f"""✨ **신규 인스타그램 공지사항 업로드**\n\n**제목:** {title}\n**본문:**\n{content}\n\n🔗 인스타그램: {post.get('post_url')}"""

    if post_id and COUNSIL_URL:
        text += f"\n📌 총홈: {COUNSIL_URL.rstrip('/')}/{post_id}"

    await destination.send(text)
    for img in images:
        await destination.send(img)

__all__ = ["bot"]
