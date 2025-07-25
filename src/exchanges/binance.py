import pandas as pd
from src.exchanges.base import Exchange
from typing import Dict, Any


class BinanceExchange(Exchange):
    def __init__(
        self,
        name: str,
        url: str,
        api_request_params: str,
        currency_pair: str,
        order_cost_total: float = 0,
    ):
        super().__init__(name, url, api_request_params, currency_pair, order_cost_total)

    def parse_snapshot_to_df(self, snapshot: Dict[str, Any]) -> pd.DataFrame:
        
        price_asks = [round(float(record[0]),8) for record in snapshot["asks"]]
        volume_asks = [round(float(record[1]),8) for record in snapshot["asks"]]
        return pd.DataFrame.from_dict({"price": price_asks, "volume": volume_asks})
