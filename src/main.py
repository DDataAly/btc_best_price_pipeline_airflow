from exchanges.binance import BinanceExchange
from exchanges.kraken import KrakenExchange
from exchanges.coinbase import CoinbaseExchange
from utils.get_best_price import find_best_price
from utils.helpers import create_best_price_df, record_best_price

import time

total_order_vol = float(input("Please enter the number of btc to buy: "))
trans_time = int(input("Please enter the desired time of purchase in sec: "))

# Does API calls to Exchanges every 10 seconds by default
num_trans_default = max(1, trans_time // 10)
num_trans_user = input(
        f"Default is {num_trans_default}."
        "Please enter another value or press Enter to accept:  "
    )

num_trans = num_trans_default if num_trans_user =='' else int(num_trans_user)
vol_per_order = total_order_vol / num_trans


def run_code(num_trans, vol_per_order, exchanges, path):
    for i in range(0, num_trans):
        best_price = find_best_price(exchanges, path, vol_per_order)
        best_price_df = create_best_price_df(best_price)
        record_best_price(best_price_df, path)
        time.sleep(trans_time / num_trans)


if __name__ == "__main__":
    kraken = KrakenExchange(
        "kraken",
        "https://api.kraken.com/0/public/Depth",
        {"pair": "XXBTZUSD", "count": 20},
        "XXBTZUSD",
    )
    binance = BinanceExchange(
        "binance",
        "https://api.binance.com/api/v3/depth",
        {"symbol": "BTCUSDT", "limit": 20},
        "BTCUSDT",
    )
    coinbase = CoinbaseExchange(
        "coinbase",
        "https://api.exchange.coinbase.com/products/BTC-USD/book",
        {"level": 2},
        "BTC-USD",
    )

    exchanges = [binance, kraken, coinbase]
    path = "/home/alyona/personal_projects/project_data_fetching/data"

    run_code(num_trans, vol_per_order, exchanges, path)
