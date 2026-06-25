from typing import Dict, Any, Optional
from api_client import APIClient
from config import Config
from logger import log

class Account:
    def __init__(self, client: APIClient):
        self.client = client

    def get_balance_and_holdings(self, symbol: str) -> Optional[Dict[str, Any]]:
        path = "/uapi/domestic-stock/v1/trading/inquire-balance"
        params = {
            "CANO": Config.ACCOUNT_CANO, "ACNT_PRDT_CD": Config.ACCOUNT_ACNT_PRDT_CD,
            "AFHR_FLPR_YN": "N", "OFL_YN": "", "INQR_DVSN": "02",
            "UNPR_DVSN": "01", "FUND_STTL_ICLD_YN": "N",
            "FNCG_AMT_AUTO_RDPT_YN": "N", "PRCS_DVSN": "01",            "CTX_AREA_FK100": "", "CTX_AREA_NK100": ""
        }
        res = self.client.request("GET", path, tr_id=Config.TR_IDS["MOCK_BALANCE"], params=params)
        if not res: return None
    
        result = {"available_cash": 0, "holding_qty": 0, "eval_amount": 0}
        try:
            if "output2" in res and len(res["output2"]) > 0:
                result["available_cash"] = int(res["output2"][0].get("dnca_tot_amt", 0))
            if "output1" in res:
                for item in res["output1"]:
                    if item.get("pdno") == symbol:
                        result["holding_qty"] = int(item.get("hldg_qty", 0))
                        result["eval_amount"] = int(item.get("evlu_amt", 0))
                        break
            log.info(f"계좌 확인 -> 예수금: {result['available_cash']}원, [{symbol}] 보유: {result['holding_qty']}주")
            return result
        except (KeyError, ValueError) as e:
            log.error(f"계좌 파싱 에러: {e}")
            return None