import os
import requests
import logging
from dotenv import load_dotenv
load_dotenv()

API_URL = os.getenv("API_URL")
API_ID = os.getenv("API_ID")
API_PW = os.getenv("API_PW")

_token = None
_group_code = None
_member_name = None

def authenticate():
    global _token, _group_code, _member_name

    payload = {
        "accountId": API_ID,
        "password": API_PW
    }
    try:
        res = requests.post(f"{API_URL}/auth/council-login", json=payload)
        if res.status_code == 200:
            data = res.json().get("data", {})
            _token = data.get("accessToken")
            _group_code = data.get("groupCodeList", [None])[0]
            _member_name = data.get("memberName")
            logging.info("🔐 로그인 성공")
        else:
            logging.error(f"❌ 로그인 실패: {res.status_code}")
    except Exception as e:
        logging.error(f"❌ 로그인 요청 중 오류: {e}")

def get_token():
    if _token is None:
        authenticate()
    return _token

def get_group_code():
    if _group_code is None:
        authenticate()
    return _group_code

def get_member_name():
    if _member_name is None:
        authenticate()
    return _member_name

def request_with_auth(method, path, **kwargs):
    token = get_token()
    if token is None:
        return None
    headers = kwargs.pop("headers", {})
    headers["Authorization"] = f"Bearer {token}"
    url = f"{API_URL}{path}"
    return requests.request(method, url, headers=headers, **kwargs)
