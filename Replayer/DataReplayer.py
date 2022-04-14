import pandas as pd

class DataReplayer:
    __slots__ = ["_data_file", "_data_frame", "_cur_index", "_df_len", "_first_ts", "_has_ended", "_cur_data"]

    def __init__(self, data_file):
        self._data_file = data_file

        self._data_frame = pd.read_csv(self._data_file)

        self._cur_index = 0
        self._cur_data = self._data_frame.iloc[0]           # this is to reduce number of ilocs for efficiency
        self._df_len = self._data_frame.shape[0]
        self._first_ts = self._data_frame["Time"].iloc[0]
        self._has_ended = False


    def get_ts_list(self):
        return self._data_frame["Time"].to_list()


    def give_data(self, ts):
        # call this function only with ts within the range
        if self._cur_index < self._df_len-1 and \
                ts == self._data_frame["Time"].iloc[self._cur_index+1]:
            self._cur_index += 1
            self._cur_data = self._data_frame.iloc[self._cur_index]

        if self._cur_index == self._df_len-1:
            self._has_ended = True

        return self._cur_data


    def next_ts(self):
        return self._data_frame["Time"].iloc[self._cur_index + 1]


    def forward_ts(self, ts):
        while self._cur_index < self._df_len-1 and \
                ts > self._data_frame["Time"].iloc[self._cur_index]:
            self._cur_index += 1
        self._cur_data = self._data_frame.iloc[self._cur_index]

        if ts > self._data_frame["Time"].iloc[self._cur_index]:
            self._has_ended = True


    def is_ready(self, ts):
        return ts >= self._first_ts


    def has_ended(self):
        return self._has_ended
 

    def reset(self):
        self._cur_index = 0
        self._has_ended = False
        self._cur_data = self._data_frame.iloc[0]
