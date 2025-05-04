# post_file.py - 이미지 업로드 요청

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
        token = login.get_token()
        headers = {"Authorization": f"Bearer {token}"}
        upload_url = f"{API_URL}/board/공지사항게시판/files"
        response = requests.post(upload_url, headers=headers, files=images)

        if response.status_code == 200:
            return response.json().get("data", {})
        else:
            logging.error(f"파일 업로드 실패: {response.status_code}")
    except Exception as e:
        logging.error(f"파일 업로드 중 오류: {e}")

    return None
