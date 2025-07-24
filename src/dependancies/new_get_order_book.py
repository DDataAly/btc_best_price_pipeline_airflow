import pprint as pp
import requests
import json
from datetime import datetime
import copy
import time
import pandas as pd
import os

def get_request_time():
    request_time = datetime.now()
    return request_time.strftime('%Y-%m-%d_%H:%M:%S')


def coinbase_reduce_snapshot_to_20_records(snapshot):
    reduced_snapshot = {
        'bids': snapshot['bids'][0:20], 
        'asks': snapshot['asks'][0:20], 
        'sequence' : snapshot['sequence'],
        'auction_mode' :snapshot['auction_mode'],
        'auction' : snapshot['auction'],
        'time': snapshot['time']
        }
    return reduced_snapshot


def find_best_price(exchanges: list, path: str, vol_per_order: float) -> list:
    request_time = get_request_time()
    for exchange in exchanges:          
        snapshot = exchange.request_order_book_snapshot()
        if exchange.name =='coinbase':   # as Coinbase sends all order book in the API request
            snapshot = coinbase_reduce_snapshot_to_20_records(snapshot)   
        exchange.save_order_book_snapshot(snapshot, path, request_time)
        price_volume_df = exchange.parse_snapshot_to_dataframe(snapshot)
        try:
            exchange.order_cost_total = exchange.calculate_order_price(price_volume_df, vol_per_order)
            prices.append((float(exchange.order_cost_total), exchange.name))
        except TypeError:
            continue
    if prices:
        prices.sort()
        best_price = list(prices[0])
        best_price.append(request_time)
        return best_price
    else:
        return ['Not available', 'Checked all exchanges', request_time]
    
        


def create_best_price_df(best_price:list) -> pd.DataFrame:
    best_price_dict = {
                        'price' : round(best_price[0],2), 
                        'exchange': best_price[1],
                        'request_time': best_price[2]
                        }
    best_price_df = pd.DataFrame([best_price_dict])
    return best_price_df


def record_best_price(best_price_df, path):
    file_name = f'{path}/best_deal.csv'
    column_headers = False if os.path.isfile(file_name) else True
    best_price_df.to_csv (file_name, mode ='a', header = column_headers, index=False)
    print ('Recording completed')
 


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

    def calculate_order_price (self, price_volume_df, vol_per_order):
        price_volume_df ['cost'] = price_volume_df['price'] * price_volume_df['volume']
        price_volume_df['cum_volume'] = price_volume_df['volume'].cumsum()

        cutoff_idx_df = price_volume_df.loc[price_volume_df['cum_volume']>=vol_per_order]
        try:
            cutoff_idx = cutoff_idx_df.index[0]
            
            if cutoff_idx == 0:  # cutoff_idx = 0 if the order could be fulfilled with the best ask in full
                order_full_cost, order_full_vol= 0,0 
            else:
                order_full_cost = price_volume_df.loc[0:cutoff_idx-1,'cost'].sum()
                order_full_vol = price_volume_df.loc[cutoff_idx-1, 'cum_volume']
            
            order_partial_vol = vol_per_order - order_full_vol
            order_partial_cost = price_volume_df.loc[cutoff_idx,'price'] * order_partial_vol
            
            order_cost_total = order_full_cost + order_partial_cost
            return order_cost_total
        except IndexError:
            print(f'The order book in {self.name} does not have enough asks to fulfill this order')




if __name__== '__main__':
    kraken = Exchange('kraken','https://api.kraken.com/0/public/Depth',{'pair':'XXBTZUSD', 'count':20}, 'XXBTZUSD')  
    binance = Exchange('binance', 'https://api.binance.com/api/v3/depth', {'symbol': 'BTCUSDT', 'limit':20}, 'BTCUSDT')  
    coinbase = Exchange('coinbase','https://api.exchange.coinbase.com/products/BTC-USD/book', {'level':2}, 'BTC-USD')
 
    exchanges = [kraken, coinbase]
    path = '/home/alyona/personal_projects/project_data_fetching/data'
    total_order_vol = 8
    num_of_transactions = 20
    vol_per_order = total_order_vol/num_of_transactions

    prices = []


    for i in range (0,num_of_transactions):
        best_price = find_best_price(exchanges, path, vol_per_order)
        best_price_df = create_best_price_df(best_price)
        record_best_price(best_price_df, path)
        time.sleep(15)



#    prices = []


#     for i in range (0,1):
#         request_time = get_request_time()
#         for exchange in exchanges:          
#             snapshot = exchange.request_order_book_snapshot()
#             exchange.save_order_book_snapshot(snapshot, path, request_time)
#             price_volume_df = exchange.parse_snapshot_to_dataframe(snapshot)
#             try:
#                 exchange.order_cost_total = exchange.calculate_order_price(price_volume_df, vol_per_order)
#                 prices.append((float(exchange.order_cost_total), exchange.name))
#                 prices.sort()
#                 best_price = list(prices[0])
#                 best_price.append(request_time)
#             except TypeError:
#                 continue
#         print (prices)    
#         print (best_price) 

#         time.sleep(5)




