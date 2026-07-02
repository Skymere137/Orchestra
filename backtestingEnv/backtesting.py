from collections import Counter
import multiprocessing
from datetime import datetime
from datetime import time
from annie_reqs import data_reqs
import heapq
import numpy as np
import pandas as pd
import math
import os
import sys
import random 
import json
import matplotlib.pyplot as plt
from strategies import MvAvgCrossover
from backtestingEnv.dataframes import EstablishDataframe
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# pd.set_option("display.max_columns", None)
# pd.set_option("display.max_rows", None)
# pd.set_option("display.width", None)
# pd.set_option("display.max_colwidth", None)

def _worker(args):
    bt, pool_chunk, min_trade = args
    return bt.create_test_pool(pool_chunk, min_trade=min_trade)

good_trades = []
bad_trades = []

def get_random_files(dir, num=1000):
    all_files = [f for f in os.listdir(dir) if os.path.isfile(os.path.join(dir, f))]

    if len(all_files) <= num:
        return all_files
    else:
        return random.sample(all_files, num)
    
# Range of trading hours to backtest on
temporal_ranges = [
    [(13, 30), (14, 0)],
    [(14, 0), (14, 30)],
    [(14, 30), (15, 0)],
    [(15, 0), (15, 30)],
    [(15, 30), (16, 0)],
    [(16, 0), (16, 30)],
    [(16, 30), (17, 0)],
    [(17, 0), (17, 30)],
    [(17, 30), (18, 0)],
    [(18, 0), (18, 30)],
    [(18, 30), (19, 0)],
    [(19, 0), (19, 30)],
    [(19, 30), (20, 0)],
    [(13, 30), (14, 30)],
    [(14, 30), (15, 30)],
    [(15, 30), (16, 30)],
    [(16, 30), (17, 30)],
    [(17, 30), (18, 30)],
    [(18, 30), (19, 30)],
    [(13, 0), (20, 0)]
]
# Dates to collect data up to
backtests_date_ranges = (
            "2026-01-01",
            "2025-10-01",
            "2025-07-01"
        )

# Backtesting Object... insert strategy
class BackTest():
    def __init__(self, strat, from_date=2):
        self.strat = strat()
        self.portfolio = 5000
        self.allowed_buying_power = self.portfolio * .2
        self.shares = 0
        self.avg_r = []

        self.from_date = backtests_date_ranges[from_date]
        self.win = 0
        self.lose = 0
        self.trades = pd.DataFrame()
        self.position = 0
        self.current_target = None
        self.current_stop = None
        self.current_entry = None

        self.file_path = "data/1m"
        self.pool = [file[:-5] for file in get_random_files(self.file_path)]
        # self.good_pool = [file[:-5] for file in os.listdir("backtestingEnv/good_stocks")]
        # self.bad_pool = [file[:-5] for file in os.listdir("backtestingEnv/bad_stocks")]
        # self.pool = np.array(self.pool)

    def run_strat(self, ticker="AAPL", min_trade=0.1, time_range=19, return_trades=False):
        self.data = data_reqs.get_data(ticker, limit=100000)
        logger.info(ticker)
        # self.data = EstablishDataframe(f"{self.file_path}/{ticker}.json")
        self.temp_range = temporal_ranges[time_range]
        self.data = self.data.data.loc[self.data.data.index > self.from_date]
        if self.data.empty:
            return None

# For loop that iterates through data rows
        trade = {}
        for ei in self.data.index:

            price = self.data.loc[ei, "close"]
            if price < self.allowed_buying_power:
# If true activate trade
                row = self.data.loc[ei]
                entry, stop, target = self.strat.make_trade_params(row, min_trade)
                if self.position == 0:
                    
                    if entry(row) is True:
                        
                        start = self.temp_range[0]
                        end = self.temp_range[1]
                                
                        if self.is_in_range(self.data.loc[ei, "timestamp"], start, end):
                            self.position = 1
                            trade["entry_time"] = ei
                            trade["entry_price"] = price
                            for key, value in self.strat.add_on_entry.items():
                                trade[key] = value
                            self.shares = math.floor(self.allowed_buying_power / price)
                            trade["num_of_shares"] = self.shares
                    
                elif self.position == 1:
                    if stop(row) is True:
                        self.position = 0
                        trade["exit_time"] = ei
                        trade["exit_price"] = price
                        trade["profit"] = (trade["exit_price"] - trade["entry_price"])
                        for key, value in self.strat.add_on_exits.items():
                            trade[key] = value
                        new_row = pd.DataFrame([trade])

                        self.trades = pd.concat([self.trades, new_row])
                        self.portfolio += trade["profit"]
                        # logger.info(self.trades)
                        trade = {}


                if self.position == 1:
                    if target(row) is True:
                        self.position = 0
                        trade["exit_time"] = ei
                        trade["exit_price"] = price
                        trade["profit"] = (trade["exit_price"] - trade["entry_price"]) * self.shares
                        for key, value in self.strat.add_on_exits.items():
                            trade[key] = value
                        new_row = pd.DataFrame([trade])

                        self.trades = pd.concat([self.trades, new_row])
                        self.portfolio += trade["profit"]
                        # logger.info(self.trades)
                        trade = {}
        win_rate = (self.trades["profit"] > 0).sum() / len(self.trades)
        print(self.portfolio, win_rate)
        return self.trades, self.data
    
    def is_in_range(self, now, start, end):
        now_time = now.time()
        start_time = time(start[0], start[1])
        end_time = time(end[0], end[1])
        if start < end:
            if start_time <= now_time <= end_time:
                return True
        return False

    def create_test_pool(self, pool, min_trade):
        total = []
        for l in pool:
            
            try:
                t, a, w, n, r = self.run_strat(l, min_trade=min_trade)
                total.append([l, a, t, w, n, r])
                self.reset()

            except Exception as e:
                print(e)
                print("Cannot retreive data from an empty dataframe")
        
        return total

    def multiprocess_testpool(self, min_trade=0.1):
        chunked = self.splitup(self.pool, 7)
        payloads = [(self, chunk, min_trade) for chunk in chunked]

        with multiprocessing.Pool(processes=7) as p:
            results = p.map(_worker, payloads)

        flattened = [row for chunk in results for row in chunk]
        for f in flattened:
            logger.info(f)
        return flattened

    def splitup(self, lst, n):
        k, m = divmod(len(lst), n)
        return [lst[i * k + min(i, m):(i + 1) * k + min(i + 1, m)] for i in range(n)]
    
    def get_top_100(self, results, idx):
        top_100 = heapq.nlargest(100, results, key=lambda x: x[idx])
        return top_100
    
    def get_ticker_pool(self):
        i = (i / 10)
        results = self.multiprocess_testpool(i)
        return results

        

    def reset(self):
        self.win = 0
        self.lose = 0

        self.position = 0
        self.current_target = None
        self.current_stop = None
        self.current_entry = None
        self.avg_r = []

        self.total_entries = 0
        self.total_exits = 0

    def compare_temp_margins(self, ticker):
        return_values = []
        min_trade = 0.03
        for t in enumerate(temporal_ranges):
            logger.info(t)
            return_values.append(self.run_strat(ticker, min_trade, t[0]))
            self.reset()
        return return_values
    
    def looped_temp_comp(self):
        values = {}
        for n in self.good_pool:
            lst_vals = self.compare_temp_margins(n)
            values[n] = []
            values[n].append({"time": lst_vals[0], "profit": lst_vals[1], "win_rate": lst_vals[2], "trades": lst_vals[3]})
            
        return values
    
# Testing directory, methods
    def compare_columns(self, col, lst1, lst2):

        n = 100
        max_n = min(len(lst1), len(lst2))

        keys1 = random.sample(list(lst1.keys()), n)
        keys2 = random.sample(list(lst2.keys()), n)

        sampled_dict1 = {k: lst1[k] for k in keys1}
        sampled_dict2 = {k: lst2[k] for k in keys2}

        good_values = []
        for name, df in sampled_dict1.items():
            temp = np.array(df[col])
            good_values.append(temp.mean())

        bad_values = []
        for name, df in sampled_dict2.items():
            temp = np.array(df[col])
            bad_values.append(temp.mean())

        good = np.array(good_values)
        bad = np.array(bad_values)
        return good.mean(), bad.mean()

    def get_best_stocks(self):
        lst = []
        for n in os.listdir("../Trading/one_min_s"):
            try:
                lst.append(self.run_strat(n[:-5]))
                self.reset()
            except:
                continue

        top_50 = heapq.nlargest(100, lst, key=lambda x: x[1])
        print(top_50)


    def delete_testing_dirs(self):
        for n in os.listdir("good_stocks"):
            os.remove(f"good_stocks/{n}")
        for n in os.listdir("bad_stocks"):
            os.remove(f"bad_stocks/{n}")
    
def convert(obj):
    """Convert non-JSON-serializable objects."""
    if isinstance(obj, np.generic):
        return obj.item()
    if isinstance(obj, tuple):
        return list(obj)
    if isinstance(obj, dict):
        return {k: convert(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [convert(i) for i in obj]
    return obj


