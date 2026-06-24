import sys
from config import Config
from logger import log
from trader import TradingSystem

def verify_environment():
    """실행 전 필수 자격 증명 환경 변수가 세팅되어 있는지 확인합니다."""
    missing_vars = []
    if not Config.APP_KEY: missing_vars.append("GH_APPKEY")
    if not Config.APP_SECRET: missing_vars.append("GH_APPSECRET")
    
    if missing_vars:
        log.critical(f"필수 환경 변수가 누락되었습니다: {', '.join(missing_vars)}")
        log.critical("시스템을 가동할 수 없어 종료합니다.")
        sys.exit(1)

if __name__ == "__main__":
    verify_environment()
    
    # 트레이딩 시스템 인스턴스화 및 구동
    ts = TradingSystem()
    ts.start()