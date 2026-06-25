import time
from datetime import datetime
from config import Config
from logger import log
from api_client import APIClient
from market_data import MarketData
from account import Account
from orders import Orders

class TradingSystem:
    def __init__(self):
        self.client = APIClient()
        self.market = MarketData(self.client)
        self.account = Account(self.client)
        self.orders = Orders(self.client)

    def is_trading_window(self) -> bool:
        """현재 시간이 지정된 거래 윈도우 시간대 내부인지 판단합니다."""
        now = datetime.now().time()
        return Config.TRADE_START_TIME <= now <= Config.TRADE_END_TIME

    def run_strategy_cycle(self):
        log.info("============ 전략 루프 사이클 시작 ============")
        
        # 1. 삼성전자 현재가 확인
        current_price = self.market.get_current_price(Config.TARGET_SYMBOL)
        if not current_price:
            log.warning("현재가 획득 실패로 이번 사이클을 건너뜁니다.")
            return

        # 2. 주문 전 계좌 상태 및 잔고 확인
        initial_balance = self.account.get_balance_and_holdings(Config.TARGET_SYMBOL)
        if not initial_balance:
            log.warning("잔고 조회 실패 - 예수금 1000만원으로 가정하고 주문을 진행합니다.")
            initial_balance = {"available_cash": 10000000, "holding_qty": 0, "eval_amount": 0}

        # 주문 가격 결정
        buy_price = current_price + Config.PRICE_OFFSET
        sell_price = current_price - Config.PRICE_OFFSET

        # 3. 보수적 시나리오 주문 테스트 (예시로 조건 충족 시 각 1주씩)
        # 실제 투자금 상황에 맞춰서 예외 처리가 가능하도록 설계
        order_triggered = False

        if initial_balance["available_cash"] >= buy_price:
            self.orders.place_order(Config.TARGET_SYMBOL, qty=1, price=buy_price, is_buy=True)
            order_triggered = True
        else:
            log.warning("예수금이 부족하여 매수 주문을 보류합니다.")

        if initial_balance["holding_qty"] > 0:
            self.orders.place_order(Config.TARGET_SYMBOL, qty=1, price=sell_price, is_buy=False)
            order_triggered = True
        else:
            log.info("보유 주식이 없어 매도 주문을 보류합니다.")

        # 4. 주문이 발생했다면, 즉시 체결 확인용 잔고 체크를 과도하게 하지 않고, 
        # 일정 간격을 둔 뒤 변동 내역을 1회 재확인합니다.
        if order_triggered:
            log.info("주문 처리 감지. 체결 추적을 위해 5초 대기 후 잔고를 확인합니다...")
            time.sleep(5)
            post_balance = self.account.get_balance_and_holdings(Config.TARGET_SYMBOL)
            
            if post_balance:
                cash_diff = post_balance["available_cash"] - initial_balance["available_cash"]
                qty_diff = post_balance["holding_qty"] - initial_balance["holding_qty"]
                log.info(f"[주문 결과 확인] 보유 수량 변동: {qty_diff}주, 예수금 변동: {cash_diff}원")

    def start(self):
        log.info("한국투자증권 모의투자 자동매매 프로그램을 시작합니다.")
        
        while True:
            if self.is_trading_window():
                try:
                    self.run_strategy_cycle()
                except Exception as e:
                    log.error(f"실행 도중 예기치 못한 크리티컬 시스템 에러 발생: {e}")
                
                log.info(f"{Config.POLLING_INTERVAL}초 동안 대기 후 다음 폴링을 진행합니다.")
                time.sleep(Config.POLLING_INTERVAL)
            else:
                now_time = datetime.now().time()
                if now_time > Config.TRADE_END_TIME:
                    log.info(f"금일 장 마감 시간({Config.TRADE_END_TIME})이 지나 프로그램을 안전하게 자동 종료합니다.")
                    break
                else:
                    log.info(f"현재 시간 {datetime.now().strftime('%H:%M:%S')}: 장 시작 대기 중 (시작 시간: {Config.TRADE_START_TIME}). 30초 후 재확인합니다.")
                    time.sleep(30)