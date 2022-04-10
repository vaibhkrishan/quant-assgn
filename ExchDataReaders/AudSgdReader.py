import urllib.request
import json

from datetime import datetime, timedelta
import time

import pandas as pd

class AudSgdReader:
    __slots__ = ["_url", "_data_file", "_data_frame"]

    def __init__(self, data_file="aud_sgd.csv"):
        self._url = "https://web-services.oanda.com/rates/api/v2/rates/spot.json?api_key=cvDTmBnDTCmIX2NRx4XT1K8l&base=sgd&quote=aud"
        self._data_frame = pd.DataFrame(columns=["Time", "Price"])
        self._data_file = data_file

        self._data_frame.to_csv(self._data_file, index=False)

    def retrieve_data(self):
        resp = urllib.request.urlopen(self._url)
        data = json.loads(resp.read())

        ts = datetime.strptime(data["meta"]["request_time"][:-6], "%Y-%m-%dT%H:%M:%S")
        ts_diff = ts - datetime(1970, 1, 1)

        price_row = {}
        price_row["Time"] = str(int(ts_diff / timedelta(microseconds=1)))
        price_row["Price"] = data["quotes"][0]["midpoint"]
 
        self._data_frame = self._data_frame.append(price_row, ignore_index=True)

    def write_data(self):
        self._data_frame.to_csv(self._data_file, mode='a', index=False, header=False)
        self._data_frame = self._data_frame.iloc[0:0]
 

def main():
    aud_sgd_reader = AudSgdReader()

    while True:
        aud_sgd_reader.retrieve_data()
        aud_sgd_reader.write_data()
        time.sleep(360)


if __name__ == "__main__":
    main()
