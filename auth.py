import json
import os
from datetime import datetime
import requests
from config import Config
from logger import log

class AuthManager:
    @staticmethod
    def get_access_token() -> str:
        """당일 유효한 토큰이 캐시에 있으면 재사용하고, 없으면 새로 발급받습니다."""
        today_str = datetime.now().strftime("%Y%m%d")
        
        # 1. 기존 캐시 확인
        if os.path.exists(Config.TOKEN_CACHE_FILE):
            try:
                with open(Config.TOKEN_CACHE_FILE, "r") as f:
                    cache = json.load(f)
                    if cache.get("date") == today_str and cache.get("token"):
                        log.info("기존에 발급된 당일 토큰을 재사용합니다.")
                        return cache["token"]
            except Exception as e:
                log.error(f"토큰 캐시 읽기 실패: {e}")

        # 2. 신규 토큰 발급
        log.info("새로운 Access Token 발급을 요청합니다.")
        url = f"{Config.BASE_URL}/oauth2/tokenP"
        headers = {"content-type": "application/json"}
        payload = {
            "grant_type": "client_credentials",
            "appkey": Config.APP_KEY,
            "secretkey": Config.APP_SECRET
        }

        try:
            response = requests.post(url, headers=headers, json=payload, timeout=5)
            response.raise_for_status()
            data = response.json()
            token = data.get("access_token")
            
            if token:
                # 파일에 캐싱
                with open(Config.TOKEN_CACHE_FILE, "w") as f:
                    json.dump({"date": today_str, "token": token}, f)
                log.info("새 토큰 발급 및 캐싱 완료.")
                return token
            else:
                raise ValueError("응답에 access_token 필드가 없습니다.")
                
        except Exception as e:
            log.error(f"토큰 발급 실패: {e}")
            raise e