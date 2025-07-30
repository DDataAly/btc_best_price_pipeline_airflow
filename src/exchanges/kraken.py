import pandas as pd
from src.exchanges.base import Exchange
from typing import Dict, Any
import logging


class KrakenExchange(Exchange):
    def __init__(
        self,
        name: str,
        url: str,
        api_request_params: str,
        currency_pair: str,
        order_cost_total: float = 0,
    ):
        super().__init__(name, url, api_request_params, currency_pair, order_cost_total)

    def validate_snapshot(self, snapshot: Dict[str, Any]) -> bool:
        if not isinstance(snapshot, dict):
            logging.error(f"{self.name}: expected a dict, got {type(snapshot)}")
            return False

        if (
            "bids" not in snapshot["result"]["XXBTZUSD"]
            or "asks" not in snapshot["result"]["XXBTZUSD"]
        ):
            logging.error(f"{self.name}: snapshot is missing bids or asks")
            return False

        if not isinstance(
            snapshot["result"]["XXBTZUSD"]["bids"], list
        ) or not isinstance(snapshot["result"]["XXBTZUSD"]["asks"], list):
            logging.error(f"{self.name}: bids or asks are not a list")
            return False

        if (
            len(snapshot["result"]["XXBTZUSD"]["bids"]) == 0
            or len(snapshot["result"]["XXBTZUSD"]["asks"]) == 0
        ):
            logging.error(f"{self.name}: bids or asks are empty lists")
            return False

        return True

    def parse_snapshot_to_df(self, snapshot: Dict[str, Any]) -> pd.DataFrame:
        # Rounded up to 8 digits to ensure full satoshi
        price_asks = [
            round(float(record[0]), 8)
            for record in snapshot["result"][self.currency_pair]["asks"]
        ]
        volume_asks = [
            round(float(record[1]), 8)
            for record in snapshot["result"][self.currency_pair]["asks"]
        ]
        return pd.DataFrame.from_dict({"price": price_asks, "volume": volume_asks})
