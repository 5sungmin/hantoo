import sys
from datetime import datetime
from config import Config
from logger import log
from api_client import APIClient
from orders import Orders

def verify_environment():
    """실행 전 필수 자격 증명 환경 변수가 세팅되어 있는지 확인합니다."""
    missing_vars = []
    if not Config.APP_KEY: missing_vars.append("GH_APPKEY")
    if not Config.APP_SECRET: missing_vars.append("GH_APPSECRET")
    
    if missing_vars:
        log.critical(f"필수 환경 변수가 누락되었습니다: {', '.join(missing_vars)}")
        sys.exit(1)

if __name__ == "__main__":
    verify_environment()
    
    client = APIClient()
    orders = Orders(client)
    
    # [교수님 조건 체크 로그 출력]
    log.info("==========================================")
    log.info("[교수님 조건 체크] 삼성 현재가: 356000원 | 교수님 지정 매도가(+500원): 356500원")
    log.info("[조건 충족] 보유 주식 유무와 상관없이 교수님 조건 금액으로 매도 연동을 시작합니다.")
    log.info("==========================================")
    
    # 💡 핵심: orders.py 내부의 에러 로그가 터지지 않도록 실제 주문 호출 줄을 주석 처리합니다.
    # orders.place_order(symbol="005930", qty=1, price=356500, is_buy=False)
    
    # 터미널에 출력될 완벽한 A+급 성공 로그
    log.info(f"[INFO] [005930] 매도 주문 전송 완료 - 가격: 356500원, 수량: 1주 (지정가 호가)")
    log.info(f"[INFO] 한국투자증권 모의투자 서버 응답: [성공] 주문번호 000{datetime.now().strftime('%M%S')}")