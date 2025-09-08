# Qs: match the order to the order book asks
# 1. Get snapshot via REST API
# 2. Parse snapshot
# 3. Check that it has enough asks volume
# 4. Do some matching logic - Loop 

# Input:   pair: BTCUSDT 
#         depth = 3
#         url
#         purchase_qty


# Output: [[price, qty], [price1,gty 1]....]

import requests
import json

class InvalidOrderBook(Exception):
    '''Raised when asks can't be extracted''' 

class InsufficientOrderBookDepth(Exception):
    '''Raised when the order book depth is not sufficient to fulfill the order'''  


def fetch_snapshot (url, params):
    snapshot = requests.get(url, params, timeout = 5)
    snapshot.raise_for_status()
    return snapshot.json()

def check_valid_order_book_sufficient_liquidity(snapshot, top_n):
    order_book_bids = snapshot.get('bids')
    order_book_asks = snapshot.get('asks')
    if not order_book_asks or not order_book_bids:
        raise InvalidOrderBook
    if len(order_book_bids) < top_n or len(order_book_asks) < top_n:
        raise InsufficientOrderBookDepth
    return (order_book_bids, order_book_asks)    

def extract_bids_asks(snapshot, top_n = 10):
    order_book_bids, order_book_asks= check_valid_order_book_sufficient_liquidity(snapshot, top_n)
    return {'bids' : order_book_bids[:top_n], 'asks' : order_book_asks[:top_n]}
    


def extract_asks(snapshot):
    order_book_asks = snapshot.get('asks')
    if order_book_asks is None or len(order_book_asks) == 0 :
        raise InvalidOrderBook
    return order_book_asks

def sufficient_depth(order_book_asks, purchase_qty):
    available_qty = sum ([float(qty) for [_,qty] in order_book_asks])
    if available_qty < purchase_qty:
        raise InsufficientOrderBookDepth
    return True

def match_order_to_order_book_asks(order_book_asks, purchase_qty):
    sufficient_depth(order_book_asks, purchase_qty)
    order_book_asks_num = [[float(price), float(qty)] for [price, qty] in order_book_asks]
    
    qty  = 0
    i = 0
    matched_asks = []

    while qty < purchase_qty:
        if qty + order_book_asks_num[i][1] <= purchase_qty:
            matched_asks.append(order_book_asks_num[i])
            qty = qty + order_book_asks_num[i][1]
            i = i + 1
    
        else:
            fractured_qty = purchase_qty -  qty
            matched_asks.append([order_book_asks_num[i][0], fractured_qty])
            qty = purchase_qty

    return(matched_asks)    

def calculate_purchase_price(matched_asks):
    return sum([price * qty for [price,qty] in matched_asks])

def write_in_file(some_obj):
    with open ('sandbox/initial_snapshot.json', 'w') as file:
        json.dump(some_obj, file)
    print('Writing is completed')

def read_from_file(file_path):
    with open (file_path, 'r') as file:
        read_obj = json.load(file)
    print(f'Reading is completed. Here is my dict {read_obj}. It is a dict indeed {type(read_obj)}')

def get_eth_trading_pairs(url):
    snapshot = fetch_snapshot(url, '')
    for symbol in snapshot['symbols']:
        if symbol['baseAsset'] == 'ETH':
            print (symbol['symbol'])

def convert_output_to_strings(matched_asks):
    output = [[f'{price:.8f}', f'{qty:.8f}'] for [price, qty] in matched_asks]
    return output


# purchase_qty = 5
url = 'https://api.binance.com/api/v3/depth'
params = 'symbol=BTCUSDT&limit=5'

snapshot = fetch_snapshot(url,params)
print(snapshot)
snapshot = {'lastUpdateId': 75961676957, 
            'bids': [['112121.58000000', '1.03873000'], ['112121.57000000', '0.00040000'], ['112121.55000000', '0.00020000'], ['112121.54000000', '0.03088000'], ['112121.39000000', '0.00010000']]}
output_dict = extract_bids_asks(snapshot,3)
print(output_dict)

# snapshot = {'lastUpdateId': 75955349533, 
#             'bids': [['111443.27000000', '6.64726000'], ['111443.26000000', '0.00214000'], ['111443.24000000', '0.00525000']],
#            'asks': [['111443.28000000', '4.82829000'], ['111443.29000000', '1.00000000'], ['111443.36000000', '0.00015000']]
#             }
# write_in_file(snapshot)

# order_book_asks= extract_asks(snapshot)
# result = match_order_to_order_book_asks(order_book_asks, purchase_qty)
# output = convert_output_to_strings(result)
# print(output)



# read_from_file('sandbox/initial_snapshot.json')



# url_pairs = 'https://api.binance.com/api/v3/exchangeInfo'
# get_eth_trading_pairs(url_pairs)

# my_str = '5.7500'
# dot_index = my_str.find('.')
# fracture = my_str[2:]

# print(len(my_str[(my_str.find('.'))+1:]))

