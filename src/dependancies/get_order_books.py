import pprint as pp
import requests
import json
from datetime import datetime
import copy
import time

def get_request_timestamp():
    request_time = datetime.now()
    return request_time.strftime('%Y-%m-%d_%H:%M:%S')


def request_order_book_snapshot(url, params):
    snapshot = requests.get(url, params).json()
    return snapshot

def coinbase_reduce_snapshot_to_20_records(snapshot):
    reduced_snapshot = copy.deepcopy(snapshot)
    reduced_snapshot['bids'] = snapshot['bids'][0:20]
    reduced_snapshot['asks'] = snapshot['asks'][0:20]
    return reduced_snapshot


def save_order_book_snapshot(snapshot, exchange_name, request_time):
    file_name = f'{exchange_name}_{str(request_time)}.json'  
    with open (file_name, 'w') as file:
        json.dump(snapshot, file)

class Exchange():
        def __init__(self, name, url, api_request_params):
            self.name = name
            self.url = url
            self.api_request_params = api_request_params

if __name__== '__main__':
    kraken = Exchange('kraken','https://api.kraken.com/0/public/Depth',{'pair':'XXBTZUSD', 'count':8})  
    binance = Exchange('binance', 'https://api.binance.com/api/v3/depth', {'symbol': 'BTCUSDT', 'limit':20})  
    coinbase = Exchange('coinbase','https://api.exchange.coinbase.com/products/BTC-USD/book', {'level':2})

    exchanges = [kraken, binance, coinbase]

    for i in range (0,2):
        request_time = get_request_timestamp()
        for exchange in exchanges:          
            snapshot = request_order_book_snapshot(exchange.url, exchange.api_request_params)
            if exchange.name == 'coinbase':
                snapshot = coinbase_reduce_snapshot_to_20_records(snapshot)
            save_order_book_snapshot(snapshot, exchange.name, request_time)
        time.sleep(5)



        
