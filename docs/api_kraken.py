import pprint
import requests
import json


# Not relevant at the moment - OHLC -  Historical data BTCUSD returned as a dataframe
"""Example of terminal output:
               time      open      high       low     close      vwap       volume  count
0  2025-07-18 10:40:00  118854.9  118949.0  118854.9  118948.9  118896.1   1.68922991    120
1  2025-07-18 10:45:00  118948.9  119137.5  118948.9  119137.5  119002.5   0.45751244    123
2  2025-07-18 10:50:00  119137.4  119200.0  119137.4  119200.0  119188.4   1.50137051    141
"""

# import pandas as pd
# request_params = {'pair':'XXBTZUSD' , 'since':1752835020, 'interval':15}
# data1 = requests.get('https://api.kraken.com/0/public/OHLC',params = request_params).json()

# time = [pd.Timestamp(record[0], unit='s') for record in data1['result']['XXBTZUSD']]
# open = [record[1] for record in data1['result']['XXBTZUSD']]
# high = [record[2] for record in data1['result']['XXBTZUSD']]
# low = [record[3] for record in data1['result']['XXBTZUSD']]
# close = [record[4] for record in data1['result']['XXBTZUSD']]
# vwap = [record[5] for record in data1['result']['XXBTZUSD']]
# volume = [record[6] for record in data1['result']['XXBTZUSD']]
# count = [record[7] for record in data1['result']['XXBTZUSD']]

# ohlc_data = {'time': time,
#              'open':open,
#              'high':high,
#              'low':low,
#              'close': close,
#              'vwap': vwap,
#              'volume':volume,
#              'count':count}

# ohlc_df = pd.DataFrame.from_dict(ohlc_data)
# print(ohlc_df)


# Not relevant at the moment - Ticker information - gets ticker information on BTCUSD  returned as a dictionary
"""Example of the terminal output:
{'a': ['119100.00000', '1', '1.000'],
 'b': ['119099.90000', '10', '10.000'],
 'c': ['119100.00000', '0.01474516'],
 'h': ['120833.70000', '120999.60000'],
 'l': ['118500.00000', '118166.80000'],
 'o': '119321.00000',
 'p': ['119767.15179', '119682.22827'],
 't': [25106, 45874],
 'v': ['670.01365505', '1294.06988512']}

 Relevant field is 'c' - Last trade closed [<price>, <lot volume>]
'a' - Ask [<price>, <whole lot volume>, <lot volume>]
'b'-Bid [<price>, <whole lot volume>, <lot volume>]
"""

data1 = requests.get("https://api.kraken.com/0/public/Ticker").json()
kraken_btc = data1["result"]["XXBTZUSD"]
pprint.pprint(kraken_btc)


# Order book of Level 2 - BTCUSD returned as a dataframe
"""
Returns up to 500 orders, default value is 100  - this set up with the count parameter
Example response:
{
  "error": [],
  "result": {
    "XXBTZUSD": {
      "asks": [
        [
          "118225.00000",
          "2.949",
          1752938894     -- timestamp 
        ]],
     "bids": [
        [
          "118221.00000",
          "0.49",
          1752938894
        ]]}
        }
}


Example output
   time_asks    price_asks volume_asks           time_bids    price_bids volume_bids
0 2025-07-18 16:04:38  117987.60000      10.563 2025-07-18 16:04:35  117987.50000       0.001
1 2025-07-18 16:04:37  117987.70000       0.063 2025-07-18 16:04:12  117979.50000       0.002
2 2025-07-18 16:04:37  117987.80000       3.752 2025-07-18 16:04:21  117975.00000       0.001
3 2025-07-18 16:04:37  117987.90000       0.117 2025-07-18 16:04:14  117967.90000       0.006
"""
import pandas as pd

request_params = {"pair": "XXBTZUSD", "count": 8}
data1 = requests.get(
    "https://api.kraken.com/0/public/Depth", params=request_params
).json()

with open("order_book_kraken.json", "w") as b:
    json.dump(data1, b)

price_asks = [record[0] for record in data1["result"]["XXBTZUSD"]["asks"]]
volume_asks = [record[1] for record in data1["result"]["XXBTZUSD"]["asks"]]
time_asks = [
    pd.Timestamp(record[2], unit="s") for record in data1["result"]["XXBTZUSD"]["asks"]
]

price_bids = [record[0] for record in data1["result"]["XXBTZUSD"]["bids"]]
volume_bids = [record[1] for record in data1["result"]["XXBTZUSD"]["bids"]]
time_bids = [
    pd.Timestamp(record[2], unit="s") for record in data1["result"]["XXBTZUSD"]["bids"]
]


order_book = {
    "time_asks": time_asks,
    "price_asks": price_asks,
    "volume_asks": volume_asks,
    "time_bids": time_bids,
    "price_bids": price_bids,
    "volume_bids": volume_bids,
}

order_book_df = pd.DataFrame.from_dict(order_book)
print(order_book_df)
