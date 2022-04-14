from bisect import bisect_left

from Replayer.DataReplayer import DataReplayer

import pandas as pd
import matplotlib.pyplot as plt

# concatenates lists from a list of lists to get a single list
def concat_lists(lists):
    return [el for sublist in lists for el in sublist]


def plot_profits(profits, slippages, avg_volumes_required, file_name):
    for cost_i in range(len(profits)):
        plt.plot(slippages, profits[cost_i], label="Avg. Vol. >= USD "+str(avg_volumes_required[cost_i]) + "K")

    plt.xlabel("Slippage(in AUD)")
    plt.ylabel("Profit(in AUD)")
    plt.title("Profit vs slippage vs 30d vol. for trading fees")

    plt.legend()
    plt.savefig(file_name)


def main():
    btc_aud_file = "ExchDataReaders/btc_aud_final.csv"
    btc_sgd_file = "ExchDataReaders/btc_sgd_final.csv"
    aud_sgd_file = "ExchDataReaders/aud_sgd.csv"

    # the transaction costs depend on 30 day volume traded
    avg_volumes_required = [1200, 4000, 10000, 20000] 
    btc_aud_tr_costs = [0.0015, 0.0013, 0.001, 0.001]
    btc_sgd_tr_costs = [0.002, 0.001, 0.0005, 0.0002]

    #avg_volumes_required = [0, 100, 300, 600, 1200, 4000, 10000, 20000] 
    #btc_aud_tr_costs = [0.0085, 0.004, 0.0025, 0.0023, 0.0015, 0.0013, 0.001, 0.001]
    #btc_sgd_tr_costs = [0.005, 0.0048, 0.004, 0.003, 0.002, 0.001, 0.0005, 0.0002]

    tr_cost_pairs = list(zip(btc_aud_tr_costs, btc_sgd_tr_costs))

    # slippages are in AUD unit
    slippages = [0.0, 0.5, 0.75, 1, 1.5, 2.5]

    btc_aud_dr = DataReplayer(btc_aud_file)
    btc_sgd_dr = DataReplayer(btc_sgd_file)
    aud_sgd_dr = DataReplayer(aud_sgd_file)

    dr_list = [btc_aud_dr, btc_sgd_dr, aud_sgd_dr]

    ts_list = concat_lists([dr.get_ts_list() for dr in dr_list])
    ts_list.sort()

    num_pairs = len(tr_cost_pairs)
    profits = []

    for cost_i in range(num_pairs):
        ts_i = 0
        last_opp_ts = 0

        ttq = 0.0
        total_profit = 0.0

        btc_aud_cost, btc_sgd_cost = tr_cost_pairs[cost_i]

        while ts_i < len(ts_list):
            ts = ts_list[ts_i]

            if not all([dr.is_ready(ts) for dr in dr_list]):
                ts_i += 1
                continue

            btc_aud_data, btc_sgd_data, aud_sgd_data = [dr.give_data(ts) for dr in dr_list]

            # if last opportunity was recently found
            # or there's too much difference in BTCAUD and BTCSGD data timestamps
            if ts - last_opp_ts < 60000000 or \
                    abs(btc_aud_data["Time"] - btc_sgd_data["Time"]) > 5000000:
                # then ignore and continue
                ts_i += 1
                continue

            aud_sgd_pr = aud_sgd_data["Price"]

            aud_sell_pr = btc_aud_data["BidP"] * (1.0-btc_aud_cost)
            aud_buy_pr = btc_aud_data["AskP"] * (1.0+btc_aud_cost)

            sgd_buy_pr = btc_sgd_data["AskP"] * aud_sgd_pr * (1.0+btc_sgd_cost)
            sgd_sell_pr = btc_sgd_data["BidP"] * aud_sgd_pr * (1.0-btc_sgd_cost)

            found_opp = False

            if aud_sell_pr > sgd_buy_pr:
                found_opp = True

                trade_qty = min(btc_aud_data["BidQ"], btc_sgd_data["AskQ"])
                ttq += trade_qty

                total_profit += (aud_sell_pr-sgd_buy_pr) * trade_qty

            if sgd_sell_pr > aud_buy_pr:
                found_opp = True

                trade_qty = min(btc_aud_data["AskQ"], btc_sgd_data["BidQ"])
                ttq += trade_qty

                total_profit += (sgd_sell_pr-aud_buy_pr) * trade_qty

            # if opportunity is found
            if found_opp:
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

        profits.append([])
        for slip in slippages:
            profits[cost_i].append(total_profit - ttq*slip)

        [dr.reset() for dr in dr_list]

    plot_profits(profits, slippages, avg_volumes_required, "Profit_plot.png")


if __name__ == "__main__":
    main()
