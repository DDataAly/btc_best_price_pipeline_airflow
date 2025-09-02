import os
from airflow.sdk import DAG
from airflow.decorators import task
from airflow.models import Variable
from datetime import datetime
from exchanges.binance import BinanceExchange
from exchanges.kraken import KrakenExchange
from exchanges.coinbase import CoinbaseExchange
from utils.get_best_price import find_best_price
from utils.helpers import create_best_price_df, record_best_price

default_args = {
    "owner": "DDataAly",
    "retries": 1,
}

with DAG(
    dag_id="btc_best_price_pipeline",
    start_date=datetime(2025, 9, 2, 12, 0),
    end_date = datetime(2025, 9, 2, 12, 5), # run for 5 mins - for testing 
    schedule_interval="@minute",  # run once per minute
    catchup=False, # don't try to re-run missed cycles between start_date and now
    default_args=default_args,
) as dag:

    @task
    def init_order_parameters():
        """
        Since it's a pipeline there is no user input => we need to initialise order parameters first.
        Uses Airflow Variables with defaults if not set.
        """
        total_order_vol = float(Variable.get("total_order_vol", default_var=0.4)) # 0.4 BTC by default
        trans_time = int(Variable.get("trans_time", default_var=30)) # 30 sec total transaction time
        num_trans = int(Variable.get("num_trans", default_var=5)) # 5 transactions within 30 sec by default

        vol_per_order = total_order_vol / num_trans

        return {
            "total_order_vol": total_order_vol,
            "trans_time": trans_time,
            "num_trans": num_trans,
            "vol_per_order": vol_per_order,
        }

    @task
    def set_up_exchanges():
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
        return [kraken, binance, coinbase]

    @task
    def run_best_price_fetch(params : dict, exchanges : list) -> float:
        total_cost = []

        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        path = os.path.join(base_dir, "data")
        os.makedirs(path, exist_ok=True)

        for i in range(params["num_trans"]):
            best_price = find_best_price(exchanges, path, params["vol_per_order"])
            best_price_df = create_best_price_df(best_price)
            record_best_price(best_price_df, path)
            total_cost.append(best_price[0])
        
        return sum(total_cost)


    params = init_order_parameters()
    exchanges = set_up_exchanges()
    total_cost = run_best_price_fetch(params, exchanges)

