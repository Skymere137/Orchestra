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

def get_random_files(dir, num=100):
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
    def __init__(self, strat, r=5, from_date=0):
        self.strat = strat(r)
        self.r = r
        self.portfolio = 1000
        self.allowed_buying_power = self.portfolio * .2
        self.shares = 0
        self.avg_r = []

        self.from_date = backtests_date_ranges[from_date]
        self.win = 0
        self.lose = 0

        self.position = 0
        self.current_target = None
        self.current_stop = None
        self.current_entry = None

        self.total_entries = 0
        self.total_exits = 0

        self.file_path = "data/1m"
        self.pool = [file[:-5] for file in get_random_files(self.file_path)]
        # self.good_pool = [file[:-5] for file in os.listdir("backtestingEnv/good_stocks")]
        # self.bad_pool = [file[:-5] for file in os.listdir("backtestingEnv/bad_stocks")]
        # self.pool = np.array(self.pool)

    def run_strat(self, ticker="NTLA", min_trade=0.03, time_range=19, return_trades=False):
        self.data = data_reqs.get_data(ticker)
        # logger.info(self.data.data)
        # self.data = EstablishDataframe(f"backtestingEnv/{self.file_path}/{ticker}.json")
        self.temp_range = temporal_ranges[time_range]
        self.levels = self.data.levels
        self.data = self.data.data.loc[self.data.data.index > self.from_date]
        if self.data.empty:
            return None

        self.data["shares"] = 0
        self.data["entry_price"] = np.nan
        self.data["exit_price"] = np.nan
        self.data["target"] = np.nan
        self.data["stop"] = np.nan
        self.data["nyields"] = np.nan
# For loop that iterates through data rows
        for ei in self.data.index:
            if self.position == 0:
                self.data.loc[ei, "shares"] = 0
            price = self.data.loc[ei, "close"]
            if price < self.allowed_buying_power:
# If true activate trade
                if self.position == 0:
                    entry, stop, target = self.strat.make_trade_params(self.data.loc[ei], self.levels)
                    if not np.isnan(entry):
                        # print(f"run_strat received: entry:{entry:.4f} stop:{stop:.4f} target:{target:.4f}")
                        # print(f"low:{self.data.loc[ei, 'low']:.4f} high:{self.data.loc[ei, 'high']:.4f}")
                        # print(f"min_trade check: {(entry - stop):.4f} >= {min_trade}")
                        # print(f"in range: {self.is_in_range(self.data.loc[ei, 'timestamp'], self.temp_range[0], self.temp_range[1])}")
                        risk = entry - stop
                        reward = target - entry
                        
                        rr = reward / risk if risk != 0 else 0
                        if self.data.loc[ei, "low"] <= entry <= self.data.loc[ei, "high"]:
                            
                            if (entry - stop) >= min_trade:
                                start = self.temp_range[0]
                                end = self.temp_range[1]
                                
                                if self.is_in_range(self.data.loc[ei, "timestamp"], start, end):

                                    self.total_entries += 1
                                    self.position = 1
                                    self.current_entry = entry
                                    self.current_stop = stop
                                    self.current_target = target
                                    self.price = self.data.loc[ei, "close"]
                                    self.shares = math.floor(self.allowed_buying_power / entry)
                                    self.avg_r.append(rr)

                                    self.data.loc[ei, "shares"] = self.shares
                                    self.data.loc[ei, "entry_price"] = entry
                                    self.data.loc[ei, "target"] = target
                                    self.data.loc[ei, "stop"] = stop
                                    self.data.loc[ei, "nyields"] = (target - entry)
    # If position is open wait til one of two exit params are true
                elif self.position == 1:
                    self.data.loc[ei, "shares"] = self.shares
                    self.data.loc[ei, "target"] = self.current_target
                    self.data.loc[ei, "stop"] = self.current_stop
                    self.data.loc[ei, "entry_price"] = self.current_entry
                    if price >= self.current_target or price <= self.current_stop:
                        if price >= self.current_target:
                            self.win += 1
                            self.data.loc[ei, "exit_price"] = self.data.loc[ei, "target"]
                        if price <= self.current_stop:
                            self.lose += 1
                            self.data.loc[ei, "exit_price"] = self.data.loc[ei, "stop"]

                        self.total_exits += 1
                        self.position = 0
                        self.current_entry = None
                        self.current_target = None
                        self.current_stop = None

                else:
                    self.data.loc[ei, "shares"] = 0
    
        self.data["profit"] = 0.0


        exit_rows = self.data["exit_price"].notna()
        
        shares = [share for share in self.data["shares"] if share > 0]

        self.data.loc[exit_rows, "profit"] = ((self.data.loc[exit_rows, "exit_price"] - self.data.loc[exit_rows, "entry_price"]) * self.data.loc[exit_rows, "shares"])

        green_trades = self.data[self.data["profit"] > 0]
        red_trades = self.data[self.data["profit"] < 0]

        self.data["wealth"] = self.data["profit"].cumsum()

        win_rate = self.win / (self.win + self.lose) if (self.win + self.lose) != 0 else 0
        
        try:
            self.avg_r = sum(self.avg_r) / len(self.avg_r)
        except:
            self.avg_r = 0
        
        gnumber = (self.data.iloc[-1]["wealth"] * self.total_entries) * win_rate
        # try:
        #     nyields = self.data["nyields"][~np.isnan(self.data["nyields"])]
        #     v = (sum(nyields) / (len(nyields) - 1))
        #     true_yield = v * ((self.avg_r * win_rate) - 1)
        #     gnumber = ((len(nyields) * true_yield))
        # except Exception as e:
        #     print(e)
        #     true_yield = None
        #     gnumber = None
        
# Calculate win rate and write data according to value of "return_trades"
        if return_trades:
            print(ticker, self.data.iloc[-1]["wealth"], win_rate, self.total_entries, self.avg_r, gnumber)
            with open("goodTrades.json", "w") as file:
                file.write(str(good_trades))
            with open("badTrades.json", "w") as file:
                file.write(str(bad_trades))
            return green_trades, red_trades
        
        return [self.data.iloc[-1]["wealth"], win_rate, self.total_entries, self.avg_r, gnumber]
    
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
                t, w, n, r, g = self.run_strat(l, min_trade=min_trade)
                total.append([l, t, w, n, r, g])
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


