from datetime import datetime
import pandas as pd
import os


def get_request_time() -> str:
    request_time = datetime.now()
    return request_time.strftime("%Y-%m-%d_%H:%M:%S")


def create_best_price_df(best_price: list) -> pd.DataFrame:
    best_price_dict = {
        "price": round(best_price[0], 2),
        "exchange": best_price[1],
        "request_time": best_price[2],
    }
    best_price_df = pd.DataFrame([best_price_dict])
    return best_price_df


def record_best_price(best_price_df: pd.DataFrame, path: str):
    file_name = f"{path}/best_deal.csv"
    col_headers = False if os.path.isfile(file_name) else True
    best_price_df.to_csv(
        file_name,
        mode="a",
        header=col_headers,
        index=False
    )
    print("Fetching new price...")
