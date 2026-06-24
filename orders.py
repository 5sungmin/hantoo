from typing import Optional, Dict, Any
from api_client import APIClient
from config import Config
from logger import log

class Orders:
    def __init__(self, client: APIClient):
        self.client = client

    def place_order(self, symbol: str, qty: int, price: int, is_buy: bool) -> Optional[Dict[str, Any]]:
        """지정가 매수/매도 주문을 제출합니다."""
        path = "/uapi/domestic-stock/v1/trading/order-cash"
        tr_id = Config.TR_IDS["MOCK_BUY"] if is_buy else Config.TR_IDS["MOCK_SELL"]
        side_str = "매수" if is_buy else "매도"
        
        payload = {
            "CANO": Config.ACCOUNT_CANO,
            "ACNT_PRDT_CD": Config.ACCOUNT_ACNT_PRDT_CD,
            "PDNO": symbol,
            "ORD_DVSN": "00",  # 00: 지정가
            "ORD_QTY": str(qty),
            "ORD_UNPR": str(price)
        }
        
        log.info(f"[{symbol}] {side_str} 주문 요청 제출 예정 -> 수량: {qty}주, 가격: {price}원")
        res = self.client.request("POST", path, tr_id=tr_id, json_data=payload)
        
        if res and "output" in res:
            order_no = res["output"].get("ODNO")
            log.info(f"[{symbol}] {side_str} 주문 성공! 주문번호: {order_no}")
            return res["output"]
        else:
            log.error(f"[{symbol}] {side_str} 주문 실패")
            return None