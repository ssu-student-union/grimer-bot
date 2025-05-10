import os
import json
import re
from instagrapi import Client
from dotenv import load_dotenv
from api import login, post_notice, post_file

load_dotenv()

INSTAGRAM_ID = os.getenv("INSTAGRAM_ID")
INSTAGRAM_PW = os.getenv("INSTAGRAM_PW")
INSTAGRAM_USERNAME = os.getenv("TARGET_INSTAGRAM_ACCOUNT")
LATEST_POST_FILE = "storage/latest_post.json"
SESSION_FILE = "storage/session.json"

def sanitize_text(text: str) -> str:
    text = re.sub(r"[\\*_`~>|#]", "", text)
    text = re.sub(r"(?m)^\s*-\s*$", "—", text)
    return text

def load_last_post():
    if os.path.exists(LATEST_POST_FILE):
        try:
            with open(LATEST_POST_FILE, "r") as f:
                return json.load(f).get("shortcode")
        except:
            return None
    return None

def save_last_post(shortcode):
    with open(LATEST_POST_FILE, "w") as f:
        json.dump({"shortcode": shortcode}, f)

def get_instagram_client():
    from instagrapi.exceptions import LoginRequired, PleaseWaitFewMinutes, ChallengeRequired
    import logging

    cl = Client()
    cl.set_locale("ko_KR")
    cl.set_country("KR")
    cl.set_timezone_offset(32400)

    def login_and_save():
        try:
            cl.login(INSTAGRAM_ID, INSTAGRAM_PW)
            # 인증 직후 바로 유저 정보로 실제 유효성 검증
            cl.user_id_from_username(INSTAGRAM_USERNAME)
            cl.dump_settings(SESSION_FILE)
            logging.info("✅ 인스타그램 로그인 성공 및 세션 저장됨")
            return cl
        except ChallengeRequired:
            logging.warning("🔐 ChallengeRequired: 이메일/SMS 인증 필요")
            cl.challenge_resolve(choice=1)
            code = input("📧 인증 코드를 입력하세요: ")
            cl.challenge_send_security_code(code)
            cl.user_id_from_username(INSTAGRAM_USERNAME)
            cl.dump_settings(SESSION_FILE)
            return cl
        except PleaseWaitFewMinutes:
            raise RuntimeError("❌ 과도한 요청. 잠시 후 다시 시도하세요.")
        except Exception as e:
            raise RuntimeError(f"❌ 로그인 실패: {e}")

    if os.path.exists(SESSION_FILE):
        try:
            cl.load_settings(SESSION_FILE)
            cl.user_id_from_username(INSTAGRAM_USERNAME)  # feed 말고 이걸로 검증
            logging.info("✅ 세션 로딩 및 인증 검증 성공")
            return cl
        except LoginRequired:
            logging.warning("⚠️ 세션 만료 → 재로그인")
            os.remove(SESSION_FILE)
            return login_and_save()
        except Exception as e:
            logging.warning(f"⚠️ 세션 불완전: {e} → 재로그인")
            os.remove(SESSION_FILE)
            return login_and_save()
    else:
        return login_and_save()


def check_new_post():
    try:
        cl = get_instagram_client()
        user_id = cl.user_id_from_username(INSTAGRAM_USERNAME)
        medias = cl.user_medias_v1(user_id, amount=1)

        if not medias:
            return {"error": "게시물이 없습니다."}

        media = medias[0]
        shortcode = media.code
        last_shortcode = load_last_post()
        if last_shortcode == shortcode:
            return None

        if last_shortcode is None:
            save_last_post(shortcode)
            return None

        content = media.caption_text or ""
        lines = content.splitlines()

        title = lines[0].strip() if lines else "제목 없음"

        # 제목 다음 줄이 공백이면 건너뜀
        if len(lines) > 1 and lines[1].strip() == "":
            body_lines = lines[2:]
        else:
            body_lines = lines[1:]

        full_content = sanitize_text("\n".join(body_lines))

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

        post_data = {
            "title": title,
            "content": full_content,
            "groupCode": login.get_group_code(),
            "memberCode": login.get_member_name(),
            "thumbNailImage": thumbnail_url,
            "isNotice": False,
            "postFileList": file_ids,
        }

        resp = post_notice.upload_instagram_post(post_data)
        post_id = resp.json().get("data", {}).get("post_id") if resp else None
        if resp and resp.status_code == 200:
            save_last_post(shortcode)

        return {
            "title": title,
            "content": full_content,
            "post_url": f"https://www.instagram.com/p/{shortcode}/",
            "images": image_urls,
            "post_id": post_id,
        }

    except Exception as e:
        return {"error": str(e)}
