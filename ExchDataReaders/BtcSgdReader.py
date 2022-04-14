import urllib.request
import json

from datetime import datetime, timedelta
import time

import pandas as pd

class BtcSgdReader:
    __slots__ = ["_url", "_data_file", "_data_frame"]

    def __init__(self, data_file="btc_sgd.csv"):
        self._url = "https://api.independentreserve.com/Public/GetOrderBook?primaryCurrencyCode=xbt&secondaryCurrencyCode=sgd"
        self._data_frame = pd.DataFrame(columns=["Time", "BidP", "BidQ", "AskP", "AskQ"])
        self._data_file = data_file

        self._data_frame.to_csv(self._data_file, index=False)

    def retrieve_data(self):
        try:
            resp = urllib.request.urlopen(self._url)
            resp_read = resp.read()
        except Exception as e:
            print(traceback.format_exc())
            exit(0)
        else:
            data = json.loads(resp_read)


        ts = datetime.strptime(data["CreatedTimestampUtc"][:-2], "%Y-%m-%dT%H:%M:%S.%f")
        ts_diff = ts - datetime(1970, 1, 1)

        top_bid = data["BuyOrders"][0]
        top_ask = data["SellOrders"][0]

        price_row = {}
        price_row["Time"] = str(int(ts_diff / timedelta(microseconds=1)))
        price_row["BidP"], price_row["BidQ"] = top_bid["Price"], top_bid["Volume"]
        price_row["AskP"], price_row["AskQ"] = top_ask["Price"], top_ask["Volume"]

        self._data_frame = self._data_frame.append(price_row, ignore_index=True)


    def write_data(self):
        self._data_frame.to_csv(self._data_file, mode='a', index=False, header=False)
        self._data_frame = self._data_frame.iloc[0:0]
 

def main():
    i = 0
    
    data_reader = BtcSgdReader()

    while True:
        time.sleep(2)
        try:
            data_reader.retrieve_data()
        except:
            print("got exception")
        else:
            i += 1

            #data_reader.write_data()
            if i%100 == 0:
                data_reader.write_data()


if __name__ == "__main__":
    main()
