from typing import Optional
from api_client import APIClient
from config import Config
from logger import log

class MarketData:
    def __init__(self, client: APIClient):
        self.client = client

    def get_current_price(self, symbol: str) -> Optional[int]:
        path = "/uapi/domestic-stock/v1/quotations/inquire-price"
        params = {"fid_cond_mrkt_div_code": "J", "fid_input_iscd": symbol}
        res = self.client.request("GET", path, tr_id=Config.TR_IDS["CURRENT_PRICE"], params=params)
        if res and "output" in res:
            try:
                price = int(res["output"]["stck_prpr"])
                log.info(f"[{symbol}] 현재가 조회 성공: {price}원")
                return price
            except (KeyError, ValueError) as e:
                log.error(f"현재가 데이터 파싱 에러: {e}")
        return None