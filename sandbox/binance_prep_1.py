# Plan:
# 1. Fetch a snapshot from Binance API
# 2. Parse it and extract asks
# 3. Need to check is the asks volume is sufficient (if not, there should be some re-fetching)
# 4. Need to calculate the price (loop logic)

# Order book: {'lastUpdateId': 75893573333, 
#           'bids': [['110675.58000000', '0.58772000'], ['110675.57000000', '0.01369000'], ['110675.50000000', '0.00005000']], 
#           'asks': [['110675.59000000', '6.58899000'], ['110675.60000000', '0.64277000'], ['110675.62000000', '0.00010000']]}

import requests

class InvalidOrderBook (Exception):
    """"Raised when order book does not contain any ask values"""

class InsufficientDepthOrderBook (Exception):
    """"Raised when order book does not have sufficient volume to fulfill the order"""    

url = 'https://api.binance.com/api/v3/depth'
params = 'symbol=BTCUSDT&limit=3'

def fetch_order_book_snapshot(url, params):
    response = requests.get(url, params, timeout = 5)
    response.raise_for_status()
    return response.json()

def extract_asks(order_book):
    if len(order_book['asks']) == 0:
        raise InvalidOrderBook ("There are no asks values")
    return order_book['asks']

def check_sufficient_volume(order_book_asks,purchase_qty):
    order_book_asks_volume = sum([float(qty) for [_,qty] in order_book_asks])
    if order_book_asks_volume < purchase_qty:
        raise InsufficientDepthOrderBook
    return True

def calculate_price(order_book_asks, purchase_qty):
    total_qty = 0
    total_price = 0
    last_item = []
    i = 0

    order_book_asks_num = [[float(price), float(qty)] for [price, qty] in order_book_asks]
    while total_qty < purchase_qty:
        total_qty = total_qty + order_book_asks_num[i][1]
        total_price = total_price + order_book_asks_num[i][1] * order_book_asks_num[i][0]
        last_item = order_book_asks_num[i]
        i=i+1
  
    if total_qty!=purchase_qty:

        last_item_total_price = last_item[0]*last_item[1]
        last_item_total_qty = last_item[1]

        total_price_full_asks = total_price - last_item_total_price
        total_qty_full_asks = total_qty - last_item_total_qty


        if purchase_qty > total_qty_full_asks:    
            fracture_qty = purchase_qty - total_qty_full_asks
        else:
            fracture_qty = purchase_qty
        fracture_price = last_item[0] * fracture_qty
            
        total_price = total_price_full_asks + fracture_price
    
    return(total_price)


order_book = {'lastUpdateId': 75893573333, 
                        'bids': [['110675.58000000', '0.58772000'], ['110675.57000000', '0.01369000'], ['110675.50000000', '0.00005000']], 
                        'asks': [['110675.59000000', '6.58899000'], ['110675.60000000', '1.0000000'], ['110675.62000000', '0.00010000']]
                    }
order_book_asks = extract_asks(order_book)
print(f'These are order_book_asks: {order_book_asks}')

purchase_qty = 7.5
print(f"Total price manual: {110675.59000000*6.58899000 +110675.60000000*(7.5-6.58899000)}")
print(calculate_price(order_book_asks, purchase_qty))

