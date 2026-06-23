# Where the dataframe instantiation objects are stored and maintained
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from datetime import datetime
# from mathematical_models.linear_regression import LinearRegression
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import math
import json
import os

# pd.set_option("display.max_columns", None)
# pd.set_option("display.max_rows", None)
# pd.set_option("display.width", None)
# pd.set_option("display.max_colwidth", None)
class EstablishDataframe:
    def __init__(self, data, _from=None):
        self.data = data
        if isinstance(self.data, str):
            self.data = pd.read_json(self.data)
        self.data = pd.DataFrame(self.data)
        if self.data.empty:
            print("❌ DataFrame is empty.")
            return
        
        if "timestamp" in self.data.columns:
            self.data["timestamp"] = pd.to_datetime(self.data["timestamp"], unit="s")
        try:
            self.data["datetime"] = pd.to_datetime(self.data["datetime"])
            self.data.set_index(["datetime"], inplace=True)
        except KeyError:
            try:
                self.data["timestamp"] = pd.to_datetime(self.data["timestamp"])
                self.data.set_index(["timestamp"], inplace=True)
            except KeyError:
                
                print("❌ 'timestamp' column not found in data. Skipping datetime conversion and indexing.")
                return

        self.data = self.data_margin(self.data)
        
        # Basic cols can be derived from basic indicators (high, low, open, close, or volume)

        required_cols = ["open", "high", "low", "close"]
        
        self.data = self.data.dropna(subset=required_cols)

        # Must be derived from stage 1 indicators
        
        self.data["sma10"] = self.data["close"].rolling(window=9).mean()
        self.data["sma50"] = self.data["close"].rolling(window=50).mean()
        self.data["sma200"] = self.data["close"].rolling(window=200).mean()

        self.data["chg%"] = (self.data["close"] - self.data["open"]).abs()
        self.data["avg_chg"] = self.data["chg%"].rolling(window=10).mean()

        # self.data["chg_std"] = self.data["chg%"].rolling(window=50).std()
        # self.data["5_min_chg"] = self.data["close"].shift(1) - self.data["open"].shift(6)
        # self.data["chg_z"] = (self.data["5_min_chg"] / self.data["chg_std"]).abs()
        

        # required_cols = ["open", "high", "low", "close", "sma10", "sma50", "chg%", "chg_std"]
        
        # self.data = self.data.dropna(subset=required_cols)


        # self.data["prob_up"] = self.sma10_pred()
        # self.data["sma10_up"] = (
        # self.data["sma10"].shift(-1) > self.data["sma10"]
        #     ).astype(int)
        # required_cols.append("prob_up")
        # required_cols.append("sma10_up")

        highs = self.data["high"]
        window_size = 11
        self.data["new_high"] = (
            highs == highs.rolling(window_size, center=True).max()
        )
        lows = self.data["low"]
        self.data["new_low"] = (
            lows == lows.rolling(window_size, center=True).min()
)       
        # self.set_trend()
        self.set_vwap()
        # self.data["price_dev"] = (self.data["close"] - self.data["close"].shift(1))
        # self.data["price_std"] = self.data["close"].rolling(10).std()
        # self.data["price_z"] = (self.data["price_dev"] / self.data["price_std"])


        # temp_lst = np.array(self.data["dev"])
        # required_cols.append("sigma")
        # self.data["dist"] = self.data["dev"] / self.data["sigma"]
        
        # self.data = self.data.dropna(subset=required_cols)
        # bins = np.linspace(0, 1, 11)
        # self.data["prob_bin"] = pd.cut(self.data["prob_up"], bins)

        # calibration = (
        #     self.data.groupby("prob_bin")["sma10_up"].mean()
        # )

        # print(calibration)0.8 * len(X_composite)
        # pred_up = (self.data["prob_up"] > 0.5).astype(int)
        # accuracy = (pred_up == self.data["sma10_up"]).mean()
        # print("Model accuracy:", accuracy)
        # df = self.data[["z_out", "sma10_delta"]].dropna()
        # self.data["prev_5"] = self.data["close"].rolling(window=5).mean()
        # self.linear_pred(lookback_window=1000, test=True)
        # self.levels = self.establish_levels()
        
# Set from and to date for data
    def data_margin(self, dataframe, _from=None):
        if _from:
            try:
                return dataframe.loc[_from: datetime.strftime(datetime.now(), "%Y-%m-%d")]
            except:

                return "Could not define dataframe range with given _from value"
        date_ranges = [
                ("2021-01-04", datetime.strftime(datetime.now(), "%Y-%m-%d")),
                ("2022-01-03", datetime.strftime(datetime.now(), "%Y-%m-%d")),
                ("2023-01-02", datetime.strftime(datetime.now(), "%Y-%m-%d")),
                ("2024-01-02", datetime.strftime(datetime.now(), "%Y-%m-%d")),
            ]
        for start_date, end_date in date_ranges:

            try:
                return dataframe.loc[start_date:end_date]
            except KeyError as e:
                print(f"KeyError: {e}. Trying next date range...")
        print("❌ No valid date range found. Returning original dataframe.")
        return dataframe

# Setting support and resistance levels   
    def establish_levels(self):
        price_std = self.data["close"].pct_change().std() * self.data["close"].mean()
        
        high_levels = self.data.loc[self.data["new_high"], "high"]
        low_levels = self.data.loc[self.data["new_low"], "low"]
        all_levels = pd.concat([high_levels, low_levels]).sort_index()

        levels = []

        for timestamp, price in all_levels.items():
            existing = next(
                (l for l in levels if abs(l["price"] - price) <= price_std),
                None
            )
            if existing:
                existing["weight"] += 1
                existing["touches"].append(timestamp)
            
            else:
                levels.append({
                    "price": price,
                    "timestamp": timestamp,
                    "weight": 1,
                    "touches": [timestamp]
                })
        return sorted(levels, key=lambda x: x["touches"][-1], reverse=True)[:10]
# VWAP method    
    def set_vwap(self):
        self.data["TPV"] = ((self.data["high"] + self.data["low"] + self.data["close"]) / 3) * self.data["volume"]
        self.data["cumtpv"] = self.data.groupby(self.data.index.date)["TPV"].cumsum()
        self.data["cumvol"] = self.data.groupby(self.data.index.date)["volume"].cumsum()
        self.data["vwap"] = self.data["cumtpv"] / self.data["cumvol"]

# Predict the next value of sma10 
    def pred_from_window(self, window, dev):
        return self.sma10_pred(window.to_numpy(), dev)
  
    def sma10_pred(self):
        returns = self.data["close"].diff().dropna()
        sorted_returns = np.sort(returns.to_numpy())

        x_out = self.data["close"].shift(9)
        x_t = self.data["close"]
        threshold = x_out - x_t

        threshold = np.array(threshold)
        idx = np.searchsorted(sorted_returns, threshold, side="right")
        prob_up = 1 - idx / len(sorted_returns)
        # percentiles = np.percentile(sorted_returns, [1, 5, 25, 50, 75, 95, 99])
        return prob_up
# Test prediction accuracy
    def return_predictions(self): 
        calibration = (
        self.data.groupby("prob_bin", observed=False)["sma10_up"].mean()
        )

        print(calibration)
        pred_up = (self.data["prob_up"] > 0.5).astype(int)
        accuracy = (pred_up == self.data["sma10_up"]).mean()
        print("Model accuracy:", accuracy)
        return accuracy, pred_up

# TESTING
    def set_trend(self):
        self.data["trend"] = 0
        current_trend = 0
        self.data["prev_trend"] = self.data["trend"].shift(1)
        
        for ei in self.data.index:
            chg_z = self.data.loc[ei, "chg_z"]
            chg_5min = self.data.loc[ei, "5_min_chg"]
            last_direction = self.data.loc[ei, "trend"]
            
            
            
