# 게시글 업로드 요청

from api import login
import logging

def upload_instagram_post(post_data):
    try:
        res = login.request_with_auth("POST", "/board/공지사항게시판/posts", json=post_data)
        return res
    except Exception as e:
        logging.error(f"❌ 게시물 전송 실패: {e}")
        return None
