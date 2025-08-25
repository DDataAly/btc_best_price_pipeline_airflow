import logging
import requests
import json
import os
import pandas as pd
from typing import Dict, Any


class Exchange:
    def __init__(
        self,
        name: str,
        url: str,
        api_request_params: str,
        currency_pair: str,
        order_cost_total: float = 0,
    ):
        self.name = name
        self.url = url
        self.api_request_params = api_request_params
        self.currency_pair = currency_pair
        self.order_cost_total = order_cost_total

    def request_order_book_snapshot(self) -> Dict[str, Any]:
        try:
            snapshot = requests.get(self.url, self.api_request_params)
            snapshot.raise_for_status()  # raises a requests.exceptions.HTTPError if the response contains a 4xx or 5xx status code.
            return snapshot.json()
        except requests.exceptions.HTTPError as e:
            logging.error(f"{self.name}: HTTP error occurred: {e}")
        except requests.exceptions.RequestException as e:
            logging.error(f"{self.name}: A request error occurred: {e}")
        return None

    def validate_snapshot(self, snapshot: Dict[str, Any]) -> bool:

        if not isinstance(snapshot, dict):
            logging.error(f"{self.name}: expected a dict, got {type(snapshot)}")
            return False

        if "bids" not in snapshot or "asks" not in snapshot:
            logging.error(f"{self.name}: snapshot is missing bids or asks")
            return False

        if not isinstance(snapshot.get("bids"), list) or not isinstance(
            snapshot.get("asks"), list
        ):
            logging.error(f"{self.name}: bids or asks are not a list")
            return False

        if len(snapshot.get("bids")) == 0 or len(snapshot.get("asks")) == 0:
            logging.error(f"{self.name}: bids or asks are empty lists")
            return False

        return True

    def trim_snapshot(self, snapshot: Dict[str, Any]) -> Dict[str, Any]:
        return snapshot

    def save_order_book_snapshot(
        self, snapshot: Dict[str, Any], path: str, request_time: str
    ):
        dir_path = os.path.join(path, self.name)
        os.makedirs(dir_path, exist_ok=True)
        file_name = os.path.join(dir_path, f"{self.name}_{str(request_time)}.json")
        with open(file_name, "w") as file:
            json.dump(snapshot, file)

    def parse_snapshot_to_df(self):
        raise NotImplementedError("Method must be implemented in subclasses")

    def calculate_order_price(
        self, price_vol_df: pd.DataFrame, vol_per_order: float
    ) -> float:
        price_vol_df["cost"] = price_vol_df["price"] * price_vol_df["volume"]
        price_vol_df["cum_volume"] = price_vol_df["volume"].cumsum()

        cutoff_idx_df = price_vol_df.loc[price_vol_df["cum_volume"] >= vol_per_order]
        try:
            cutoff_idx = cutoff_idx_df.index[0]

            # cutoff_idx = 0 if the order could be fulfilled with the best ask in full
            if cutoff_idx == 0:
                order_full_cost, order_full_vol = 0, 0
            else:
                order_full_cost = price_vol_df.loc[: cutoff_idx - 1, "cost"].sum()
                order_full_vol = price_vol_df.loc[cutoff_idx - 1, "cum_volume"]

            order_partial_vol = vol_per_order - order_full_vol
            order_partial_cost = (
                price_vol_df.loc[cutoff_idx, "price"] * order_partial_vol
            )

            order_cost_total = order_full_cost + order_partial_cost
            return round(order_cost_total, 8)
        except IndexError:
            logging.error(
                f"The order book in {self.name}"
                " does not have enough asks to fulfill this order"
            )
