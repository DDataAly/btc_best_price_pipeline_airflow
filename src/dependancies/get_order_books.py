import pprint as pp
import requests
import json
from datetime import datetime
import copy
import time
import pandas as pd
import numpy as np

def get_request_time():
    request_time = datetime.now()
    return request_time.strftime('%Y-%m-%d_%H:%M:%S')


def coinbase_reduce_snapshot_to_20_records(snapshot):
    reduced_snapshot = copy.deepcopy(snapshot)
    reduced_snapshot['bids'] = snapshot['bids'][0:20]
    reduced_snapshot['asks'] = snapshot['asks'][0:20]
    return reduced_snapshot

def record_best_price(best_deal_price_exchange, request_time, path):
    file_name = f'{path}/order_split.csv'
    record = [request_time, best_deal_price_exchange[1], best_deal_price_exchange[0]]
    record_df = pd.DataFrame(record)
    record_df.to_csv (file_name, mode ='a')


class Exchange():
    def __init__(self, name, url, api_request_params, currency_pair, order_price = 0):
        self.name = name
        self.url = url
        self.api_request_params = api_request_params
        self.currency_pair = currency_pair
        self.order_price = order_price

    def request_order_book_snapshot(self):
        snapshot = requests.get(self.url, self.api_request_params).json()
        return snapshot


    def save_order_book_snapshot(self, snapshot, path, request_time):
        file_name = f'{path}/{self.name}/{self.name}_{str(request_time)}.json'  
        if self.name =='coinbase':
            snapshot = coinbase_reduce_snapshot_to_20_records(snapshot)    
        with open (file_name, 'w') as file:
            json.dump(snapshot, file)


    def parse_snapshot_to_dataframe (self, snapshot):
        if self.name == 'kraken':
            price_asks = [record[0] for record in snapshot['result'][self.currency_pair]['asks']]
            volume_asks = [record[1] for record in snapshot['result'][self.currency_pair]['asks']]

        if self.name == 'coinbase':
            price_asks = [record[0] for record in snapshot['asks']]
            volume_asks = [record[1] for record in snapshot['asks']]

        if self.name == 'binance':
            price_asks = [record[0] for record in snapshot['asks']]
            volume_asks = [record[1] for record in snapshot['asks']]
        
        price_volume = {
                    'price_asks': price_asks,
                    'volume_asks':volume_asks
                    }
        price_volume_df = pd.DataFrame.from_dict(price_volume)
        return price_volume_df

    def calculate_order_price (self, price_volume_df, order_volume):
        price_volume_df['cum_volume'] = price_volume_df['volume_asks'].cumsum()
        top_of_range_index = np.where(price_volume_df['cum_volume'] > order_volume). min()
        top_of_range_cum_volume = price_volume_df.get_value(top_of_range_index, 'cum_volume')
        price_volume_df.loc[price_volume_df['cum_volume'] <= top_of_range_cum_volume, '' ]
        pass
        return self.order_price
    




if __name__== '__main__':
    kraken = Exchange('kraken','https://api.kraken.com/0/public/Depth',{'pair':'XXBTZUSD', 'count':20}, 'XXBTZUSD')  
    binance = Exchange('binance', 'https://api.binance.com/api/v3/depth', {'symbol': 'BTCUSDT', 'limit':20}, 'BTCUSDT')  
    coinbase = Exchange('coinbase','https://api.exchange.coinbase.com/products/BTC-USD/book', {'level':2}, 'BTC-USD')

    exchanges = [kraken, binance, coinbase]
    path = '/home/alyona/personal_projects/project_data_fetching/data'
    order_volume = 0.01
    prices = []


    for i in range (0,2):
        request_time = get_request_time()
        for exchange in exchanges:          
            snapshot = exchange.request_order_book_snapshot()
            exchange.save_order_book_snapshot(snapshot, path, request_time)
            exchange.order_price = exchange.calculate_order_price(exchange.parse_snapshot_to_dataframe, order_volume)
            prices.append((exchange.order_price, exchange.name))
        best_deal_price_exchange = prices.sort()[0]    
        time.sleep(5)






