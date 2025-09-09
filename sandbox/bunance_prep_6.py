# Match the sell order to the order book and calculate best price
# Input : trading pair, sale_qty, url, order book depth
# Output: matched_bids = [[price:str, qty:str], [price1:str, qty1:str]] in .:8f formst
# best_price = float

# 1. Get order book copy - okay to assume response?
# 2. Extract bids and convert them to num
# 3. Sufficient depth of the order book
# 4. Match logic - ensure correct format
# 5. Calculate best_price
# 6. Record output in a file

# {
#   "lastUpdateId": 1027024,
#   "bids": [ ["114500.00000000","0.52000000"],["114448.00000000","1.17000000"],["114442.00000000","1.20000000"]],
#   "asks": [["114550","0.0100000"],["114600","1.3300000"],["114700","2.20000000"]]
# }

import requests
import json
import bisect

class InvalidOrderBook(Exception):
  '''Raised when the order book missing 'bids' key or values'''

class InsufficientDepth(Exception):
  '''Raised when the order book doesn't have enough bids to fill the order'''


def fetch_order_book(url, params):
  snapshot = requests.get(url, params, timeout = 5)
  snapshot.raise_for_status()
  return snapshot.json()

def extract_bids(snapshot):
  bids = snapshot.get('bids')
  if not bids:
    raise InvalidOrderBook
  return [[float(price), float(qty)] for [price, qty] in bids]


def check_suficient_depth(snapshot, sell_qty):
  bids = extract_bids(snapshot)
  total_vol = sum([qty for [_,qty] in bids])
  if sell_qty > total_vol:
    raise InsufficientDepth
  return True  

def match_order (snapshot, sell_qty):
  bids = extract_bids(snapshot)
  check_suficient_depth(snapshot, sell_qty)

  total_matched_qty = 0
  i= 0
  matched_bids =[]

  while total_matched_qty < sell_qty:
    if sell_qty < total_matched_qty + bids[i][1]:
      fracture_qty = sell_qty - total_matched_qty
      matched_bids.append([bids[i][0], round(fracture_qty,8)])
      return matched_bids
    
    else:
      total_matched_qty = total_matched_qty + bids[i][1]
      matched_bids.append(bids[i])  
      i = i +1
  return matched_bids

def calculate_best_price(matched_bids):
  return round((sum ([price*qty for [price,qty] in matched_bids])),2)

def format_match(matched_bids):
  output = [[f'{price:.8f}', f'{volume:.8f}'] for [price, volume] in matched_bids]
  return output

def save_in_file(best_price):
  with open('src/best_deal.json', 'w') as file:
    json.dump (({'best price' : best_price}), file)


def read_from_file(path):
  with open(path, 'r') as file:
    result = json.load(file)
  return result


def extract_bids_asks(snapshot):
  bids = snapshot.get('bids')
  asks = snapshot.get('asks')
  if not bids or not asks:
    raise InvalidOrderBook
  return (bids, asks)

def return_top_n(snapshot, n):
  bids, asks = extract_bids_asks(snapshot)
  top_n_bids = bids[0:n]
  top_n_asks = asks[0:n]
  return ({'bids':top_n_bids}, {'asks':top_n_asks})

def confirm_sorting_order(bids, asks):
  bids_num_price = [[float(price)] for [price,qty] in bids]
  asks_num_price = [[float(price)] for [price,qty] in asks]

  bids_checker = all([True if bids_num_price[i+1] < bids_num_price[i] else False for i in range (0,2)])
  return bids_checker

def find_item_index(bids:list, new_bid):
  bids_prices = [price for [price, _] in bids]
  bids_prices_reversed = bids_prices[::-1]
  for i in range (0,len(bids)):
    if bids_prices_reversed[i]==new_bid[0]:
      return i    

def update_bid_in_order_book(bids, new_bid):
  bids_reversed = bids [::-1]
  bids_prices = [price for [price, _] in bids]
  bids_prices_reversed = bids_prices[::-1]
  
  index =  find_item_index (bids, new_bid)

  if not index:
    bisect.insort_left(bids_reversed, new_bid)

  if index and new_bid[1] == 0:
    bids_reversed.pop(index)

  if index and new_bid[1] != 0:
    bids_reversed[index][1] = new_bid[1]

  updated_bids = bids_reversed[::-1]

  return(updated_bids)



sell_qty = 1.1
snapshot = {
  "lastUpdateId": 1027024,
  "bids": [ ["114500","0.52000000"],["114448","1.17000000"],["114442","1.20000000"]],
  "asks": [["114550","0.0100000"],["114600","1.3300000"],["114700","2.20000000"]]}

new_bid =   [114448,0.0000000]
bids = extract_bids(snapshot)
print(bids)

index = find_item_index(bids, new_bid)
print(index)

updated_bids = update_bid_in_order_book(bids, new_bid)
print(updated_bids)


# print(bids)
# matched_bids = match_order(snapshot, sell_qty)
# print(matched_bids)
# print(f'Expected value: {114500*0.52 + 114448*0.5800000000000001}')
# best_price = calculate_best_price(matched_bids)
# save_in_file(best_price)

# result = read_from_file('src/best_deal.json')
# print(f'This is result {result}')

# print(format_match(matched_bids))

# output = return_top_n(snapshot, 2)
# print(f'These are top 2 bids and asks {output}')

# bids, asks = extract_bids_asks(snapshot)
# bids_checker = confirm_sorting_order(bids, asks)
# print(bids_checker)
