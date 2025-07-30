import pandas as pd
from src.exchanges.base import Exchange
from typing import Dict, Any


class CoinbaseExchange(Exchange):
    def __init__(
        self,
        name: str,
        url: str,
        api_request_params: str,
        currency_pair: str,
        order_cost_total: float = 0,
    ):
        super().__init__(name, url, api_request_params, currency_pair, order_cost_total)

    def trim_snapshot(self, snapshot: Dict[str, Any]) -> Dict[str, Any]:
        num_records = 20
        trimmed_snapshot = {
            "bids": snapshot["bids"][: num_records + 1],
            "asks": snapshot["asks"][: num_records + 1],
            "sequence": snapshot["sequence"],
            "auction_mode": snapshot["auction_mode"],
            "auction": snapshot["auction"],
            "time": snapshot["time"],
        }
        return trimmed_snapshot

    def parse_snapshot_to_df(self, snapshot: Dict[str, Any]) -> pd.DataFrame:
        # Rounded up to 8 digits to ensure full satoshi
        price_asks = [round(float(record[0]), 8) for record in snapshot["asks"]]
        volume_asks = [round(float(record[1]), 8) for record in snapshot["asks"]]
        return pd.DataFrame.from_dict({"price": price_asks, "volume": volume_asks})
