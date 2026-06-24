import os
from datetime import time
from dotenv import load_dotenv

# 환경 변수 로드 (.env 파일 또는 시스템 환경 변수)
load_dotenv()

class Config:
    # 인증 정보
    ACCOUNT_FULL = os.getenv("GH_ACCOUNT", "12345678-01")
    # 한국투자증권 계좌는 보통 '8자리-2자리' 구조입니다.
    ACCOUNT_CANO = ACCOUNT_FULL.split("-")[0] if "-" in ACCOUNT_FULL else ACCOUNT_FULL[:8]
    ACCOUNT_ACNT_PRDT_CD = ACCOUNT_FULL.split("-")[1] if "-" in ACCOUNT_FULL else ACCOUNT_FULL[8:10] or "01"
    
    APP_KEY = os.getenv("GH_APPKEY", "")
    APP_SECRET = os.getenv("GH_APPSECRET", "")

    # API 도메인 설정 (모의투자 서버)
    BASE_URL = "https://openapivts.koreainvestment.com:29443"
    
    # 토큰 캐시 파일 경로
    TOKEN_CACHE_FILE = "token_cache.json"

    # 대상 종목 정보 (삼성전자)
    TARGET_SYMBOL = "005930"
    PRICE_OFFSET = 2000  # 현재가 대비 매수/매도 호가 차이 (2,000원)

    # 매매 시간 설정
    TRADE_START_TIME = time(9, 10)
    TRADE_END_TIME = time(15, 30)
    
    # 폴링 인터벌 (모의투자 제한을 고려해 보수적으로 10초 설정)
    POLLING_INTERVAL = 10 

    # KIS API 거래 ID (TR_ID) 정의 - 수정이 용이하도록 격리
    TR_IDS = {
        "CURRENT_PRICE": "FHKST01010100",  # 국내주식현재가 시세
        "MOCK_BUY": "VTTC0846U",           # 모의투자 현물매수주문
        "MOCK_SELL": "VTTC0845U",          # 모의투자 현물매도주문
        "MOCK_BALANCE": "VTTC8434R"        # 모의투자 주식잔고조회
    }