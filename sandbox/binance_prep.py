"""
Qs: fine total cost of buying 0.5 BTC on market price
Input: currency, url, order book depth
Output: total cost (float)

1) fetch order book snapshot 
2) convert it to Python dict
3) extract asks
4) check the total qty of asks is more than 0.5 BTC 
5) if not 4: increase order book depth and fetch another snapshot
6) calculate price of 0.5 BTC - tbc if we want to extract prices only and use a queue

Snapshot format:{
'lastUpdateId': 75837685819, 
'bids': [['112486.91000000', '4.08508000'], ['112486.90000000', '0.00075000'], ['112486.74000000', '0.00005000']], 
'asks': [['112486.92000000', '12.57763000'], ['112486.93000000', '0.00336000'], ['112487.20000000', '0.00013000']]
}
"""

import requests
import json

class InvalidOrderBookException(Exception):
    def __init__(self, message = 'Order book does not have asks'):
        self.message = message
        super().__init__(self)

class InsufficientOrderBookDepth(Exception):
    """Order book depth is not sufficient to fill this order"""

def fetch_order_book_snapshot(url, params):
    response = requests.get(url, params)
    return response

def convert_snapshot_to_json(response):
    order_book = response.json()
    return order_book

def extract_order_book_asks (order_book):
    order_book_asks = order_book.get('asks')
    if order_book_asks is None:
        raise InvalidOrderBookException
    return order_book_asks

def check_sufficient_asks_volume (order_book_asks, purchase_qty):
    ask_volumes = [float(qty) for [_, qty] in order_book_asks]
    return True if sum(ask_volumes) >= purchase_qty else False

def extract_relevant_asks(order_book_asks, purchase_qty):
    if check_sufficient_asks_volume(order_book_asks, purchase_qty):
        best_asks_qty = 0 
        i = 0
        best_asks_price_qty = []
        while best_asks_qty < purchase_qty:
            ask_volumes_prices = [[float(price),float(qty)] for [price, qty] in order_book_asks]
            best_asks_price_qty.append(ask_volumes_prices[i])
            best_asks_qty = best_asks_qty + ask_volumes_prices[i][1]
            i=i+1
        return best_asks_price_qty
    else:
        raise InsufficientOrderBookDepth


def calculate_best_price(best_asks_price_qty, purchase_qty):
    if len(best_asks_price_qty) == 1:
        total_cost = sum([price * purchase_qty for [price, qty] in best_asks_price_qty])
    else:
        full_best_asks_price_qty = best_asks_price_qty[0:(len(best_asks_price_qty)-1)]
        full_asks_cost = sum([price * qty for [price, qty] in full_best_asks_price_qty])
        full_asks_qty = sum(qty for [price,qty] in full_best_asks_price_qty)
             
        fracture_best_asks_price = best_asks_price_qty[-1][0]
        fracture_qty = purchase_qty - full_asks_qty
        fracture_asks_costs = fracture_best_asks_price * fracture_qty

        total_cost = full_asks_cost + fracture_asks_costs
    return total_cost


currency_pair = 'BTCUSDT'
order_book_depth = 3
purchase_qty = 2
payload = f'symbol={currency_pair}&limit={order_book_depth}'
url ='https://api.binance.com/api/v3/depth'

response = fetch_order_book_snapshot(url,payload)
order_book = convert_snapshot_to_json(response)
print(order_book)
order_book_asks = extract_order_book_asks (order_book)
best_asks_price_qty = extract_relevant_asks(order_book_asks, purchase_qty)
total_cost = calculate_best_price(best_asks_price_qty, purchase_qty)
print(total_cost)













































# import json
# import requests

# url = 'https://api.binance.com/api/v3/depth'
# payload = {'symbol': 'ETH','limit': 8}

# bymbol='symbol=ETHGBP&limit=1'

# def get_order_book_snapshot(url,payload):
#     response = requests.get(url, params = payload)
#     result = response.json()
#     return result

# result = get_order_book_snapshot(url, bymbol)    
# print(result)
# print(type(result))

# url2= 'https://api.binance.com/api/v3/exchangeInfo'
# response = requests.get(url2)
# result = response.json().get('symbols')
# print(type(result))
# for _ in range (0, len(result)):
#     print(result[_]['symbol'])

