import requests

class InsufficientOrderBookDepth(Exception):
    """"Raised when the order book snapshot doesn't have enough depth to fulfill the order"""

class InvalidOrderBookFormat(Exception):
    """Raised when the snapshot doesn't have 'asks' key ot it's value is empty"""
def fetch_exchange_info(url, params = ''):
    response = requests.get(url, params, timeout = 5)
    response.raise_for_status()
    return response.json()

def return_trading_symbols(snapshot):
    for symbol in snapshot['symbols']:
        if ('XRP' in symbol['symbol']) and ('USD' in symbol['symbol']):
            print (symbol['symbol'])

def extract_asks(snapshot):
    if snapshot is None:
        raise InvalidOrderBookFormat
    order_book_asks =  snapshot.get('asks')
    if order_book_asks is None or len(order_book_asks) == 0:
        raise InvalidOrderBookFormat
    return order_book_asks

def check_sufficient_depth (order_book_asks, purchase_qty):
    asks_volume = sum([float(qty) for [_,qty] in order_book_asks])
    if asks_volume < purchase_qty:
        raise InsufficientOrderBookDepth
    return True

def match_order_with_order_book(order_book_asks, purchase_qty):
    order_book_asks_num = [[float(price),float(qty)] for [price,qty] in order_book_asks]
    matched_asks = []
    total_qty = 0
    i = 0

    while total_qty < purchase_qty:
        total_qty = total_qty + order_book_asks_num[i][1]

        if total_qty > purchase_qty and len(matched_asks) == 0:
            matched_asks.append([order_book_asks_num[i][0], purchase_qty])

        elif total_qty > purchase_qty:
            total_qty = total_qty - order_book_asks_num[i][1]
            matched_asks.append([order_book_asks_num[i][0], purchase_qty-total_qty ])
            total_qty = total_qty + order_book_asks_num[i][1]

        else:
            matched_asks.append([order_book_asks_num[i][0], order_book_asks_num[i][1]])
            i = i+1
    
    return matched_asks


def calculate_totals(matched_asks):
    total_qty = sum([qty for [_,qty] in matched_asks])
    total_price = sum ([qty * price for [price, qty] in matched_asks])
    return (total_qty, total_price)




url = 'https://api.binance.com/api/v3/depth'
params = 'symbol=BTCUSDT&limit=3'
purchase_qty = 14
response = fetch_exchange_info(url, params = params)
response = {
'lastUpdateId': 75837685819, 
'bids': [['112486.91000000', '4.08508000'], ['112486.90000000', '0.00075000'], ['112486.74000000', '0.00005000']], 
'asks': []
}
order_book_asks =  extract_asks(response)
#order_book_asks = [['110200.00000000', '3.70614000'], ['110200.01000000', '1.00030000'], ['110200.15000000', '2.00010000']]
if check_sufficient_depth(order_book_asks, purchase_qty):
    print(order_book_asks)
    matched_asks = match_order_with_order_book(order_book_asks, purchase_qty)
    print(matched_asks)
    total_qty, total_price = calculate_totals(matched_asks)
    print(total_qty)
    print(f'This is manual price {110200.00000000*3.70614000+110200.01000000*1.00030000+110200.15000000*(5-1.00030000-3.70614000)}')
    print(total_price)



















# url = 'https://api.binance.com/api/v3/exchangeInfo'
# response = fetch_exchange_info(url)
# return_trading_symbols(response)



# url = 'https://api.binance.com/api/v3/depth'
# params = 'symbol=XRPUSDT&limit=3'
# print(fetch_exchange_info(url, params = params))


