import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from backtestingEnv import backtesting
from strategies import MvAvgCrossover

class LinearRegression:
    def __init__(self):
        self.slope = None
        self.intercept = None
        self.r_squared = None
    
    def fit(self, x, y):
        
        try:
            x = np.array(x, dtype=float)
            y = np.array(y, dtype=float)
        except:
            print(y)
        x_mean = x.mean()
        y_mean = y.mean()

        numerator = np.sum((x - x_mean) * (y - y_mean))
        denominator = np.sum((x - x_mean)**2)

        self.slope = numerator / denominator

        self.intercept = y_mean - self.slope * x_mean

        y_pred = self.predict(x)
        ss_total = np.sum((y - y_mean)**2)
        ss_residual = np.sum((y - y_pred)**2)
        self.r_squared = 1 - (ss_residual / ss_total)

        return self

    def predict(self, x):
        return self.slope * x + self.intercept

    def plot(self, x, y):
        plt.figure(figsize=(10,6))
        plt.scatter(x, y, color='blue', label='Data points')
        plt.xlim(min(x), max(x))
        plt.show()

def plotting_trades(test, ticker):
        good_trades, bad_trades = test.run_strat(ticker, return_trades=True)
        good_df = pd.DataFrame(good_trades)
        bad_df = pd.DataFrame(bad_trades)
        price_df = test.data
        # print(price_df["prob_up"])

        if price_df['timestamp'].dtype == 'int64':
            price_df['timestamp'] = pd.to_datetime(price_df['timestamp'], unit='ms')

        if 'timestamp' in good_df.columns and good_df['timestamp'].dtype == 'int64':
            good_df['timestamp'] = pd.to_datetime(good_df['timestamp'], unit='ms')

        if 'timestamp' in bad_df.columns and bad_df['timestamp'].dtype == 'int64':
            bad_df['timestamp'] = pd.to_datetime(bad_df['timestamp'], unit='ms')

        plt.figure(figsize=(14, 6))

        plt.plot(price_df['timestamp'], price_df['sma10'], label="Price", linewidth=1)
        plt.plot(price_df['timestamp'], price_df['sma50'], label="Price", linewidth=1)

        if len(good_df) > 0:
            plt.scatter(
                good_df['timestamp'],
                good_df['exit_price'],
                color='green',
                s=40,
                label="Good Trades",
                zorder=5
            )
            plt.scatter(
                good_df['timestamp'],
                good_df['entry_price'],
                color='blue',
                s=40,
                label="Bad Trades",
                zorder=5
            )

        if len(bad_df) > 0:
            plt.scatter(
                bad_df['timestamp'],
                bad_df['exit_price'],
                color='red',
                s=40,
                label="Bad Trades",
                zorder=5
            )
            plt.scatter(
                bad_df['timestamp'],
                bad_df['entry_price'],
                color='blue',
                s=40,
                label="Bad Trades",
                zorder=5
            )

        plt.title(f"Trades for {ticker}")
        plt.xlabel("Time")
        plt.ylabel("Price")
        plt.legend()
        plt.grid(True, alpha=0.3)

        plt.tight_layout()
        plt.show()
