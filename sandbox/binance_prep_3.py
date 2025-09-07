import requests
import json

def fetch_snapshot(url, params):
    response = requests.get(url, params, timeout = 5)
    response.raise_for_status()
    return response.json()

def save_snapshot(snapshot):
    with open ('sandbox/initial_snapshot.json', 'w') as file:
        json.dump (snapshot, file)
    print('Snapshot saved')    


def read_initial_snapshot():
    with open ('sandbox/initial_snapshot.json', 'r') as file:
        new_object = json.load(file)
    return new_object    

url = 'https://api.binance.com/api/v3/depth'
params='symbol=BTCUSDT&limit=3'
snapshot = fetch_snapshot(url, params)
print(snapshot)

save_snapshot(snapshot)
new_object= read_initial_snapshot()
print (f'Here is the new object :{new_object}. It\'s type is {type(new_object)}')
