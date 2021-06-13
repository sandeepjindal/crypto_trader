from binance.client import Client
import configparser
import pandas as pd
from datetime import timedelta, datetime
import os.path
import math
from dateutil import parser
# Loading keys from config file
config = configparser.ConfigParser()
ordersConfig = configparser.ConfigParser()

config.read_file(open('secret.cfg'))
ordersConfig.read_file(open('orders.cfg'))
print(ordersConfig)
test_api_key = config.get('BINANCE', 'TEST_API_KEY')
test_secret_key = config.get('BINANCE', 'TEST_SECRET_KEY')

client = Client(test_api_key, test_secret_key)

client.API_URL = 'https://api.binance.com/api'  # To change endpoint URL for test account

#info = client.get_account()  # Getting account info

### CONSTANTS
binsizes = {"1m": 1, "5m": 5, "1h": 60, "1d": 1440}
batch_size = 750




### FUNCTIONS
def minutes_of_new_data(symbol, kline_size, data, source):
    if len(data) > 0:  old = parser.parse(data["timestamp"].iloc[-1])
    elif source == "binance": old = datetime.strptime('1 Jan 2017', '%d %b %Y')

    if source == "binance": new = pd.to_datetime(client.get_klines(symbol=symbol, interval=kline_size)[-1][0], unit='ms')

    return old, new

def get_all_binance(symbol, kline_size, save = False):
    filename = '%s-%s-data.csv' % (symbol, kline_size)
    if os.path.isfile(filename): data_df = pd.read_csv(filename)
    else: data_df = pd.DataFrame()
    oldest_point, newest_point = minutes_of_new_data(symbol, kline_size, data_df, source = "binance")
    delta_min = (newest_point - oldest_point).total_seconds()/60
    available_data = math.ceil(delta_min/binsizes[kline_size])
    oldest_point= datetime.strptime('01 Jan 2020', '%d %b %Y')
    if oldest_point == datetime.strptime('26 Apr 2021', '%d %b %Y'): print('Downloading all available %s data for %s. Be patient..!' % (kline_size, symbol))
    else: print('Downloading %d minutes of new data available for %s, i.e. %d instances of %s data.' % (delta_min, symbol, available_data, kline_size))
    klines = client.get_historical_klines(symbol, kline_size, oldest_point.strftime("%d %b %Y %H:%M:%S"), newest_point.strftime("%d %b %Y %H:%M:%S"))
    data = pd.DataFrame(klines, columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'quote_av', 'trades', 'tb_base_av', 'tb_quote_av', 'ignore' ])
    data['timestamp'] = pd.to_datetime(data['timestamp'], unit='ms')
    if len(data_df) > 0:
        temp_df = pd.DataFrame(data)
        data_df = data_df.append(temp_df)
    else: data_df = data
    data_df.set_index('timestamp', inplace=True)
    if save: data_df.to_csv(filename)
    print('Processing Complete.!')

    return data_df

def place_orders():
    print(ordersConfig)

if __name__ == "__main__":
    get_all_binance("BNBUSDT","1d",save=True)