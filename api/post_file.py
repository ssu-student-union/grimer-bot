import requests
import logging
import os
from api import login

API_URL = os.getenv("API_URL")

def upload_images(image_urls):
    images = []

    for idx, url in enumerate(image_urls):
        try:
            res = requests.get(url)
            filename = f"image{idx}.jpg"
            file_tuple = (filename, res.content, 'image/jpeg')
            images.append(("images", file_tuple))
        except Exception as e:
            logging.warning(f"이미지 다운로드 실패: {url} - {e}")

    if not images:
        logging.warning("업로드할 이미지가 없습니다.")
        return None

    try:
        upload_url_path = "/board/공지사항게시판/files"
        response = login.request_with_auth("POST", upload_url_path, files=images)

        if response and response.status_code == 200:
            return response.json().get("data", {})
        else:
            logging.error(f"파일 업로드 실패: {response.status_code if response else '응답 없음'}")
    except Exception as e:
        logging.error(f"파일 업로드 중 오류: {e}")

    return None
