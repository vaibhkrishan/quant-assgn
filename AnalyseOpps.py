from bisect import bisect_left

import sys

from Replayer.DataReplayer import DataReplayer

import pandas as pd
import matplotlib.pyplot as plt

# concatenates lists from a list of lists to get a single list
def concat_lists(lists):
    return [el for sublist in lists for el in sublist]


def main():
    btc_aud_file = "ExchDataReaders/btc_aud_final.csv"
    btc_sgd_file = "ExchDataReaders/btc_sgd_final.csv"
    aud_sgd_file = "ExchDataReaders/aud_sgd.csv"

    btc_aud_cost = 0.001
    btc_sgd_cost = 0.0002

    btc_aud_dr = DataReplayer(btc_aud_file)
    btc_sgd_dr = DataReplayer(btc_sgd_file)
    aud_sgd_dr = DataReplayer(aud_sgd_file)

    dr_list = [btc_aud_dr, btc_sgd_dr, aud_sgd_dr]

    ts_list = concat_lists([dr.get_ts_list() for dr in dr_list])
    ts_list.sort()

    ts_i = 0
    last_opp_ts = 0
    opp_count = 0

    opps = []
    trades = []
 
    while ts_i < len(ts_list):
        ts = ts_list[ts_i]

        if not all([dr.is_ready(ts) for dr in dr_list]):
            ts_i += 1
            continue

        btc_aud_data, btc_sgd_data, aud_sgd_data = [dr.give_data(ts) for dr in dr_list]

        if ts - last_opp_ts < 60000000 or \
                abs(btc_aud_data["Time"] - btc_sgd_data["Time"]) > 5000000:
            ts_i += 1
            continue

        aud_sgd_pr = aud_sgd_data["Price"]

        btc_aud_bid, btc_aud_ask = btc_aud_data["BidP"], btc_aud_data["AskP"]
        btc_sgd_bid, btc_sgd_ask = btc_sgd_data["BidP"], btc_sgd_data["AskP"]

        aud_sell_pr = btc_aud_bid * (1.0-btc_aud_cost)
        aud_buy_pr = btc_aud_ask * (1.0+btc_aud_cost)

        sgd_buy_pr = btc_sgd_ask * aud_sgd_pr * (1.0+btc_sgd_cost)
        sgd_sell_pr = btc_sgd_bid * aud_sgd_pr * (1.0-btc_sgd_cost)

        found_opp = False

        if aud_sell_pr > sgd_buy_pr:
            found_opp = True

            trade_qty = min(btc_aud_data["BidQ"], btc_sgd_data["AskQ"])

            opp = {}
            opp["Time"] = ts
            opp["AUDSide"] = "Sell"
            opp["SellP"] = btc_aud_bid
            opp["BuyP"] = btc_sgd_ask
            opp["AUDSGDPrice"] = aud_sgd_pr
            opp["AUDSpread"] = btc_aud_ask - btc_aud_bid
            opp["SGDSpread"] = btc_sgd_ask - btc_sgd_bid
            opp["TradeQty"] = trade_qty
            opps.append(opp)

            if opp_count % 36 == 0:
                trade = {}
                trade["Time"] = ts
                trade["AUDSide"] = "Sell"
                trade["SellP"] = btc_aud_bid
                trade["BuyP"] = btc_sgd_ask
                trade["AUDSGDPrice"] = aud_sgd_pr
                trade["TradeQty"] = trade_qty
                trade["TradingFees"] = trade_qty * (btc_aud_bid * btc_aud_cost + \
                        btc_sgd_ask * btc_sgd_cost * aud_sgd_pr)
                trade["Profit"] = aud_sell_pr - sgd_buy_pr
                trades.append(trade)

        if sgd_sell_pr > aud_buy_pr:
            found_opp = True

            trade_qty = min(btc_aud_data["AskQ"], btc_sgd_data["BidQ"])

            opp = {}
            opp["Time"] = ts
            opp["AUDSide"] = "Buy"
            opp["SellP"] = btc_sgd_bid
            opp["BuyP"] = btc_aud_ask
            opp["AUDSGDPrice"] = aud_sgd_pr
            opp["AUDSpread"] = btc_aud_ask - btc_aud_bid
            opp["SGDSpread"] = btc_sgd_ask - btc_sgd_bid
            opp["TradeQty"] = trade_qty
            opps.append(opp)

            if opp_count % 36 == 0:
                trade = {}
                trade["Time"] = ts
                trade["AUDSide"] = "Buy"
                trade["SellP"] = btc_sgd_bid
                trade["BuyP"] = btc_aud_ask
                trade["AUDSGDPrice"] = aud_sgd_pr
                trade["TradeQty"] = trade_qty
                trade["TradingFees"] = trade_qty * (btc_aud_ask * btc_aud_cost + \
                        btc_sgd_bid * btc_sgd_cost * aud_sgd_pr)
                trade["Profit"] = sgd_sell_pr - aud_buy_pr
                trades.append(trade)

        # if opportunity is found
        if found_opp:
            opp_count += 1

            last_opp_ts = ts

            # then move both data frames forward by at least one index
            # this avoids duplicate opportunities from being captured
            ts = max(dr_list[0].next_ts(), dr_list[1].next_ts())

            [dr.forward_ts(ts) for dr in dr_list]
            ts_i = bisect_left(ts_list, ts)

        else:
            ts_i += 1

        if any([dr.has_ended() for dr in dr_list]):
            break

    opp_df = pd.DataFrame(opps)
    opp_df = opp_df.set_index("Time")
    opp_df.to_csv("opportunities.csv")
 
    trade_df = pd.DataFrame(trades)
    trade_df = trade_df.set_index("Time")
    trade_df.to_csv("sample_trades.csv")


if __name__ == "__main__":
    main()
