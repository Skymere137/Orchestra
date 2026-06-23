import pandas as pd
import numpy as np
from annie_reqs import data_reqs as req
import logging
from matplotlib import pyplot as plt

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TICKER = "IONQ"

df = req.get_data(TICKER, "1d")

def run_test():
    money = 500
    counter = 0

    df.data["position"] = 0
    df.data["profit"] = 0
    df.data["prev_close"] = df.data["close"].shift(1)
    for ei in df.data.index:
        sma50 = df.data.loc[ei, "sma50"]
        sma200 = df.data.loc[ei, "sma200"]
        close = df.data.loc[ei, "close"]
        prev_close = df.data.loc[ei, "prev_close"]

        # if counter % 10 == 0:
        #     check_params(df.data.loc)ei, 
        if sma50 >= sma200:
            df.data.loc[ei, "position"] = 1
            
        elif sma50 < sma200:
            df.data.loc[ei, "position"] = 0
            
        if df.data.loc[ei, "position"] == 1:
            df.data.loc[ei, "profit"] = ((close - prev_close) * (money // close))
            
            print(money)
        money += df.data.loc[ei, "profit"]

        counter += 1
    print(df.data["profit"].cumsum())
    return df.data
        
def test_investment():
    counter = 0

    df.data["position"] = 0
    df.data["profit"] = 0
    df.data["prev_close"] = df.data["close"].shift(1)
    current_position = 0
    print(df.data.index.is_unique)
    print(df.data.index.duplicated().sum())
    for ei in df.data.index:
        
        close = df.data.loc[ei, "close"]
        prev_close = df.data.loc[ei, "prev_close"]

        if counter % 30 == 0:
            current_position += 1
            
        df.data.loc[ei, "profit"] = ((close - prev_close) * current_position)
        counter += 1
        df.data.loc[ei, "position"] = current_position
    return df.data

def plot_mv_avg_crossover(data: pd.DataFrame) -> None:
    data = data.copy()
    data["ma50"] = data["close"].rolling(50).mean()
    data["ma200"] = data["close"].rolling(200).mean()

    # find crossover points
    data["prev_ma50"] = data["ma50"].shift(1)
    data["prev_ma200"] = data["ma200"].shift(1)

    golden_cross = data[(data["ma50"] > data["ma200"]) & (data["prev_ma50"] <= data["prev_ma200"])]
    death_cross = data[(data["ma50"] < data["ma200"]) & (data["prev_ma50"] >= data["prev_ma200"])]

    plt.figure(figsize=(14, 7))
    plt.plot(data.index, data["close"], label="Close", color="gray", linewidth=1, alpha=0.6)
    plt.plot(data.index, data["ma50"], label="50 MA", color="blue", linewidth=1.5)
    plt.plot(data.index, data["ma200"], label="200 MA", color="orange", linewidth=1.5)

    plt.scatter(golden_cross.index, golden_cross["ma50"], color="green", marker="^", zorder=5, s=100, label="Golden Cross")
    plt.scatter(death_cross.index, death_cross["ma50"], color="red", marker="v", zorder=5, s=100, label="Death Cross")

    plt.title("50/200 MA Crossover")
    plt.xlabel("Date")
    plt.ylabel("Price")
    plt.legend()
    plt.tight_layout()
    plt.show()
