import urllib.request
import json

import pandas as pd

class BtcAudReader:
    __slots__ = ["_url", "_data_file", "_data_frame"]

    def __init__(self, data_file="btc_aud.csv"):
        self._url = "https://api.btcmarkets.net/v3/markets/BTC-AUD/orderbook"
        self._data_frame = pd.DataFrame(columns=["Time", "BidP", "BidQ", "AskP", "AskQ"])
        self._data_file = data_file

        self._data_frame.to_csv(self._data_file, index=False)


    def retrieve_data(self):
        resp = urllib.request.urlopen(self._url)
        data = json.loads(resp.read())

        price_row = {}
        price_row["Time"] = data["snapshotId"]
        price_row["BidP"], price_row["BidQ"] = data["bids"][0]
        price_row["AskP"], price_row["AskQ"] = data["asks"][0]

        self._data_frame = self._data_frame.append(price_row, ignore_index=True)


    def write_data(self):
        self._data_frame.to_csv(self._data_file, mode='a', index=False, header=False)
        self._data_frame = self._data_frame.iloc[0:0]
 

def main():
    i = 0
 
    data_reader = BtcAudReader()

    while True:
        data_reader.retrieve_data()
        i += 1

        if i%100 == 0:
            data_reader.write_data()


if __name__ == "__main__":
    main()
