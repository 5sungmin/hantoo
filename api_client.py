import time
from typing import Dict, Any, Optional
import requests
from config import Config
from auth import AuthManager
from logger import log

class APIClient:
    def __init__(self):
        self.token: Optional[str] = None

    def _get_headers(self, tr_id: str) -> Dict[str, str]:
        if not self.token:
            self.token = AuthManager.get_access_token()
            
        return {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.token}",
            "appkey": Config.APP_KEY,
            "appsecret": Config.APP_SECRET,
            "tr_id": tr_id,
            "custtype": "P"  # 개인 고객 기본값
        }

    def request(self, method: str, path: str, tr_id: str, params: Optional[Dict[str, Any]] = None, json_data: Optional[Dict[str, Any]] = None, retries: int = 2) -> Optional[Dict[str, Any]]:
        """네트워크 타임아웃 및 재시도 로직을 포함한 공통 요청 메서드"""
        url = f"{Config.BASE_URL}{path}"
        headers = self._get_headers(tr_id)
        
        for attempt in range(retries + 1):
            try:
                if method.upper() == "GET":
                    response = requests.get(url, headers=headers, params=params, timeout=5)
                else:
                    response = requests.post(url, headers=headers, json=json_data, timeout=5)
                
                # 호출 속도 제한(Rate Limit) 완화를 위한 미세 대기
                time.sleep(0.2)
                
                response.raise_for_status()
                return response.json()
                
            except requests.exceptions.RequestException as e:
                log.warning(f"[{attempt + 1}/{retries + 1}] API 요청 실패 (TR_ID: {tr_id}): {e}")
                if attempt < retries:
                    time.sleep(1)
                else:
                    log.error(f"최종 요청 실패 (TR_ID: {tr_id})")
                    return None