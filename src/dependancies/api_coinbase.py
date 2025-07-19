import pprint as pp
import requests
import json

# Order book - could be Level 1 - Level 3 - BTCUSD returned as a dataframe 

'''
Level 2 provides aggregated view, use Level 3 for information on the individual orders

Response format:
{
  "sequence": 13051505638,  -- this is the order book snapshot number, ie number of the last order added to the book 
  "bids": [
    [
      "6247.58",
      "6.3578146",
      2    -- number of bids at this price
    ]
  ],
  "asks": [
    [
      "6251.52",
      "2",
      1
    ]
  ],
  "time": "2021-02-12T01:09:23.334Z"
}


Example output
       price_asks volume_asks
0         118222.61  0.00850559
1         118225.57  0.01268761
2          118226.9  0.08091421
3         118226.91  0.03116366
4         118228.45  0.03060686
'''
import pandas as pd
request_params = {'level':2}
data1 = requests.get('https://api.exchange.coinbase.com/products/BTC-USD/book', params = request_params).json()

# This is recording all order book in memory - is this what we want? 13088 asks records returned
with open ('order_book_coinbase.json','w') as b:
    json.dump(data1,b)

price_asks = [record[0] for record in data1['asks']]
volume_asks = [record[1] for record in data1['asks']]

time_order_book_snapshot = [data1['time']]

price_bids = [record[0] for record in data1['bids']]
volume_bids = [record[1] for record in data1['bids']]

order_book = {
            'price_asks': price_asks,
            'volume_asks':volume_asks
            }

order_book_df = pd.DataFrame.from_dict(order_book)
print(order_book_df)
