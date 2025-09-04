import json
import requests

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

url2= 'https://api.binance.com/api/v3/exchangeInfo'
response = requests.get(url2)
result = response.json().get('symbols')
print(type(result))
for _ in range (0, len(result)):
    print(result[_]['symbol'])

