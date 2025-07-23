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
    def __init__(self, name, url, api_request_params, currency_pair, order_cost_total = 0):
        self.name = name
        self.url = url
        self.api_request_params = api_request_params
        self.currency_pair = currency_pair
        self.order_cost_total = order_cost_total

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
            price_asks = [float(record[0]) for record in snapshot['result'][self.currency_pair]['asks']]
            volume_asks = [float(record[1]) for record in snapshot['result'][self.currency_pair]['asks']]

        if self.name == 'coinbase':
            price_asks = [float(record[0]) for record in snapshot['asks']]
            volume_asks = [float(record[1]) for record in snapshot['asks']]

        if self.name == 'binance':
            price_asks = [float(record[0]) for record in snapshot['asks']]
            volume_asks = [float(record[1]) for record in snapshot['asks']]
        
        price_volume = {
                    'price': price_asks,
                    'volume': volume_asks
                    }
        price_volume_df = pd.DataFrame.from_dict(price_volume)
        return price_volume_df

    def calculate_order_price (self, price_volume_df, order_volume):
        price_volume_df ['cost'] = price_volume_df['price'] * price_volume_df['volume']
        price_volume_df['cum_volume'] = price_volume_df['volume'].cumsum()

        cutoff_idx_df = price_volume_df.loc[price_volume_df['cum_volume']>=order_volume]
        try:
            cutoff_idx = cutoff_idx_df.index[0]
            
            if cutoff_idx == 0:  # cutoff_idx = 0 if the order could be fulfilled with the best ask in full
                order_full_cost, order_full_vol= 0,0 
            else:
                order_full_cost = price_volume_df.loc[0:cutoff_idx-1,'cost'].sum()
                order_full_vol = price_volume_df.loc[cutoff_idx-1, 'cum_volume']
            
            order_partial_vol = order_volume - order_full_vol
            order_partial_cost = price_volume_df.loc[cutoff_idx,'price'] * order_partial_vol
            
            order_cost_total = order_full_cost + order_partial_cost
            return order_cost_total
        except IndexError:
            print('The order book does not have enough asks to fulfill this order')


if __name__== '__main__':
    kraken = Exchange('kraken','https://api.kraken.com/0/public/Depth',{'pair':'XXBTZUSD', 'count':20}, 'XXBTZUSD')  
    binance = Exchange('binance', 'https://api.binance.com/api/v3/depth', {'symbol': 'BTCUSDT', 'limit':20}, 'BTCUSDT')  
    coinbase = Exchange('coinbase','https://api.exchange.coinbase.com/products/BTC-USD/book', {'level':2}, 'BTC-USD')

    exchanges = [kraken, binance, coinbase]
    path = '/home/alyona/personal_projects/project_data_fetching/data'
    order_volume = 0.5
    prices = []


    for i in range (0,1):
        request_time = get_request_time()
        for exchange in exchanges:          
            snapshot = exchange.request_order_book_snapshot()
            exchange.save_order_book_snapshot(snapshot, path, request_time)
            price_volume_df = exchange.parse_snapshot_to_dataframe(snapshot)

            exchange.order_cost_total = exchange.calculate_order_price(price_volume_df, order_volume)
            prices.append((exchange.order_cost_total, exchange.name))
        print (prices)    
        time.sleep(5)



