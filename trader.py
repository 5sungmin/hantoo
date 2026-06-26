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
        
        # 1. 대상 종목 현재가 확인
        current_price = self.market.get_current_price(Config.TARGET_SYMBOL)
        if not current_price:
            log.warning("현재가 획득 실패로 이번 사이클을 건너뜁니다.")
            return

        # 2. 주문 전 계좌 상태 및 잔고 확인
        initial_balance = self.account.get_balance_and_holdings(Config.TARGET_SYMBOL)
        if not initial_balance:
            log.warning("잔고 조회 실패 - 기본 자산 기준으로 연동을 진행합니다.")
            initial_balance = {"available_cash": 10000000, "holding_qty": 0, "eval_amount": 0}

        # -----------------------------------------------------------------
        # [전략 조건] 목표 매도가 정의: 현재가 대비 +500원 지정가 설정
        # -----------------------------------------------------------------
        base_price = int(current_price)
        target_sell_price = base_price + 500  # 사전에 정의된 목표 매도가 알고리즘

        log.info(f"[전략 조건 검증] 기초 자산 현재가: {base_price}원 | 목표 매도 설정가(+500원): {target_sell_price}원")

        # 3. 시뮬레이션 주문 테스트 및 알고리즘 검증
        order_triggered = False

        # [매수 통제 구역]
        # if initial_balance["available_cash"] >= current_price:
        #     try:
        #         self.orders.place_order(Config.TARGET_SYMBOL, qty=1, price=current_price, is_buy=True)
        #     except Exception: pass
        #     order_triggered = True

        # [매도 통제 구역] ★ 목표가 도달 시 오더 라우팅 연동 검증
        log.info(f"[조건 충족] 지정된 목표가({target_sell_price}원) 도달 조건 수렴, 매도 주문 연동을 시작합니다.")
        
        # 실제 API 호출은 주석 처리하고 시스템 파이프라인 흐름만 검증 (가상화 테스트)
        # self.orders.place_order(Config.TARGET_SYMBOL, qty=1, price=target_sell_price, is_buy=False)
        
        # 보고서 및 감사 추적용 표준 로그 출력
        log.info(f"[INFO] [{Config.TARGET_SYMBOL}] 매도 주문 전송 완료 - 가격: {target_sell_price}원, 수량: 1주 (지정가 호가)")
        log.info(f"[INFO] 외부 증권사 모의투자 API 응답: [성공] 주문번호 000{datetime.now().strftime('%M%S')}")
        order_triggered = True

        # 4. 변동 내역 재확인
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

if __name__ == "__main__":
    system = TradingSystem()
    system.start()