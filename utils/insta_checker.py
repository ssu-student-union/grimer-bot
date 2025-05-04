import os
import json
import logging
from instagrapi import Client
from dotenv import load_dotenv
from api import login, post_notice, post_file

load_dotenv()

INSTAGRAM_ID = os.getenv("INSTAGRAM_ID")
INSTAGRAM_PW = os.getenv("INSTAGRAM_PW")
INSTAGRAM_USERNAME = os.getenv("TARGET_INSTAGRAM_ACCOUNT")
LATEST_POST_FILE = "storage/latest_post.json"
SESSION_FILE = "storage/session.json"

def load_last_post():
    if os.path.exists(LATEST_POST_FILE):
        try:
            with open(LATEST_POST_FILE, "r") as f:
                data = json.load(f)
                shortcode = data.get("shortcode")
                if shortcode:
                    return shortcode
        except json.JSONDecodeError:
            logging.warning("⚠️ latest_post.json 파싱 실패")
    return None

def save_last_post(shortcode):
    with open(LATEST_POST_FILE, "w") as f:
        json.dump({"shortcode": shortcode}, f)

def get_instagram_client():
    cl = Client()
    if os.path.exists(SESSION_FILE):
        cl.load_settings(SESSION_FILE)
        try:
            cl.login(INSTAGRAM_ID, INSTAGRAM_PW)
        except Exception:
            logging.warning("⚠️ 세션 로그인 실패, 재로그인 시도 중...")
            cl.set_locale("ko_KR")
            cl.set_country("KR")
            cl.set_timezone_offset(32400)
            cl.login(INSTAGRAM_ID, INSTAGRAM_PW)
            cl.dump_settings(SESSION_FILE)
    else:
        cl.login(INSTAGRAM_ID, INSTAGRAM_PW)
        cl.dump_settings(SESSION_FILE)
    return cl

def check_new_post():
    try:
        cl = get_instagram_client()
        user_id = cl.user_id_from_username(INSTAGRAM_USERNAME)
        medias = cl.user_medias_v1(user_id, amount=1)

        if not medias:
            return {"error": "게시물이 없습니다."}

        media = medias[0]
        shortcode = media.code
        is_first_run = not os.path.exists(LATEST_POST_FILE)
        last_shortcode = load_last_post()

        # ✅ 최초 실행이면 저장만 하고 전송 안 함
        if is_first_run or last_shortcode is None:
            logging.info(f"🆕 최초 실행 - 게시물 저장만 수행됨: {shortcode}")
            save_last_post(shortcode)
            return None

        if last_shortcode == shortcode:
            return None  # 새 게시물 아님

        # 🔹 게시물 내용 추출
        content = media.caption_text or ""
        lines = [line.strip() for line in content.splitlines() if line.strip()]
        title = lines[0] if lines else "제목 없음"
        title = title[:50] if len(title) > 50 else title
        full_content = "\n".join(lines[1:]) if len(lines) > 1 else ""

        # 🔹 이미지 처리
        image_urls = []
        if media.thumbnail_url:
            image_urls.append(media.thumbnail_url)
        elif hasattr(media, "resources"):
            image_urls = [r.thumbnail_url for r in media.resources if r.thumbnail_url]

        file_ids, thumbnail_url = [], None
        if image_urls:
            result = post_file.upload_images(image_urls)
            if result:
                file_ids = [f["id"] for f in result.get("postFiles", [])]
                thumbnail_url = result.get("thumbnailUrl")

        # 🔹 공지 데이터 생성
        post_data = {
            "title": title,
            "content": full_content,
            "groupCode": login.get_group_code(),
            "memberCode": login.get_member_name(),
            "thumbNailImage": thumbnail_url,
            "isNotice": False,
            "postFileList": file_ids
        }

        resp = post_notice.upload_instagram_post(post_data)
        if resp and resp.status_code == 200:
            save_last_post(shortcode)

        return {
            "title": title,
            "content": full_content,
            "post_url": f"https://www.instagram.com/p/{shortcode}/",
            "images": image_urls
        }

    except Exception as e:
        logging.error(f"Instagram 크롤링 오류: {e}")
        return {"error": str(e)}
