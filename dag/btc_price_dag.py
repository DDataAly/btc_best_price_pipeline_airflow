from airflow.sdk import DAG
from airflow.decorators import task
from airflow.models import Variable
from datetime import datetime

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
    def init_parameters():
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


    params = init_parameters()



