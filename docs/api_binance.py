import pprint as pp
import requests
import json
import pandas as pd


# Order book - Level 2 only - BTC-USD returned as a dataframe
"""
Limit specifies the required depth of the order book, ie number of orders returned.
The default limit is 100 which has weight 5; permitted rate is 1200 weight per minute
Response format:
{
  "lastUpdateId": 1027024,
  "bids": [
    [
      "4.00000000",     // PRICE
      "431.00000000"    // QTY
    ]
  ],
  "asks": [
    [
      "4.00000200",
      "12.00000000"
    ]
  ]
}

Output format:
     price_asks volume_asks
0   117804.22000000  1.12963000
1   117804.79000000  0.00005000
2   117804.80000000  0.02015000
3   117804.89000000  0.00005000
4   117804.90000000  0.02015000
"""

request_params = {"symbol": "BTCUSDT", "limit": 20}
data1 = requests.get(
    "https://api.binance.com/api/v3/depth", params=request_params
).json()
pp.pprint(data1)

with open("order_book_binance.json", "w") as b:
    json.dump(data1, b)

price_asks = [record[0] for record in data1["asks"]]
volume_asks = [record[1] for record in data1["asks"]]

order_book = {"price_asks": price_asks, "volume_asks": volume_asks}

order_book_df = pd.DataFrame.from_dict(order_book)
print(order_book_df)
