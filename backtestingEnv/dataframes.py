# Where the dataframe instantiation objects are stored and maintained
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
# import operator
from datetime import datetime
from backtestingEnv.charting import LinearRegression
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

        self.data["sma10"] = self.data["close"].rolling(window=10).mean()
        self.data["sma50"] = self.data["close"].rolling(window=50).mean()

        # self.data["chg%"] = (self.data["close"] - self.data["open"]).abs()
        # self.data["chg_sigma"] = self.data["chg%"].rolling(window=50).std()

        required_cols = ["open", "high", "low", "close", "sma10", "sma50"]
        
        self.data = self.data.dropna(subset=required_cols)


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
        self.set_vwap()
        self.data["price_dev"] = (self.data["close"] - self.data["close"].shift(1))
        self.data["price_std"] = self.data["close"].rolling(10).std()
        self.data["price_z"] = (self.data["price_dev"] / self.data["price_std"])


        # temp_lst = np.array(self.data["dev"])
        # required_cols.append("sigma")
        # self.data["dist"] = self.data["dev"] / self.data["sigma"]
        
        # self.data = self.data.dropna(subset=required_cols)
        # bins = np.linspace(0, 1, 11)
        # self.data["prob_bin"] = pd.cut(self.data["prob_up"], bins)

        # calibration = (
        #     self.data.groupby("prob_bin")["sma10_up"].mean()
        # )

        # print(calibration)
        # pred_up = (self.data["prob_up"] > 0.5).astype(int)
        # accuracy = (pred_up == self.data["sma10_up"]).mean()
        # print("Model accuracy:", accuracy)
        # df = self.data[["z_out", "sma10_delta"]].dropna()
        self.data["prev_5"] = self.data["close"].rolling(window=5).mean()
        self.levels = self.establish_levels()
        
        # for l in self.levels:
        #     print(f"{l} \n")
# TESTING
    def linear_pred(self, window_size=5):
        stock_prices = np.array(self.data["close"])

        X, y = [], []
        for i in range(len(stock_prices) - window_size):
            X.append(stock_prices[i:i+window_size])
            y.append(stock_prices[i+window_size])

        X = np.array(X)
        y = np.array(y)

        X_features = X.mean(axis=1)
        
        # print(f"X_features shape: {X_features.shape}")
        # print(f"y shape: {y.shape}")
        # print(f"X_features dtype: {X_features.dtype}")
        # print(f"y dtype: {y.dtype}")

        model = LinearRegression()
        model.fit(range(len(X_features)), X_features)

        print(f"Slope: {model.slope}")
        print(f"Intercept: {model.intercept}")
        print(f"R-squared: {model.r_squared}")

        last_index = len(X_features)
        future_periods = np.array(range(last_index, last_index + 5))
        future_predictions = model.predict(future_periods)
        model.plot(X_features, y)
        print(f"Future Price Predictions: {future_predictions}")


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
    
    def set_vwap(self):
        self.data["TPV"] = ((self.data["high"] + self.data["low"] + self.data["close"]) / 3) * self.data["volume"]
        self.data["cumtpv"] = self.data.groupby(self.data.index.date)["TPV"].cumsum()
        self.data["cumvol"] = self.data.groupby(self.data.index.date)["volume"].cumsum()
        self.data["vwap"] = self.data["cumtpv"] / self.data["cumvol"]

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
        percentiles = np.percentile(sorted_returns, [1, 5, 25, 50, 75, 95, 99])
        return prob_up

    def return_predictions(self): 
        calibration = (
        self.data.groupby("prob_bin", observed=False)["sma10_up"].mean()
        )

        print(calibration)
        pred_up = (self.data["prob_up"] > 0.5).astype(int)
        accuracy = (pred_up == self.data["sma10_up"]).mean()
        print("Model accuracy:", accuracy)
        return accuracy, pred_up



# print(
#     df.data.loc["2025-10-28":"2025-10-31"]
#            .between_time("13:30:00", "14:30:00")
# )
# df.data["sma10_prediction"].hist(bins=30)
# plt.title("Histogram of distribution")
# plt.xlabel("chg%")
# plt.ylabel("Frequency")
# plt.show()