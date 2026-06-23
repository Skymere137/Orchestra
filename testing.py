import os
import random
import pandas as pd
import numpy as np
from backtestingEnv import backtesting
from strategies import MvAvgCrossover
import matplotlib.pyplot as plt
from mathematical_models.linear_regression import LinearRegression
from backtestingEnv.dataframes import EstablishDataframe
from strategies import ProbabilityCrossover
from strategies import UptrendingBounce
from strategies import MvAvgCrossover
from backtestingEnv import backtesting
from annie_reqs import data_reqs
from backtestingEnv import charting
from backtestingEnv import mv_avg_backtest

# pd.set_option("display.max_columns", None)
# pd.set_option("display.max_rows", None)
# pd.set_option("display.width", None)
# pd.set_option("display.max_colwidth", None)

# df = data_reqs.get_data("NTLA", tf="1m", limit=10000)


# print(new_df.linear_pred(5))
# print(type(df.data.iloc[0]["timestamp"]))
# print(type(new_df.data.iloc[0]["timestamp"]))
df = mv_avg_backtest.df
mv_avg_backtest.plot_mv_avg_crossover(df.data)
def experiment_one():
    strat = MvAvgCrossover
    backtest = backtesting.BackTest(strat)

    stats = backtest.multiprocess_testpool()
    tickers = [n[0] for n in stats]
    data = data_reqs.experiment_one(tickers)
    profits = {n[0]: n[1] for n in stats}

    for entry in data:
        for symbol, fields in entry.items():
            if symbol in profits:
                fields["Profit"] = {
                    "label": "Profit",
                    "value": str(profits[symbol])
                }

    charting.plot_marketcap_vs_yield(data)

def experiment_two():
    strat = MvAvgCrossover
    backtest = backtesting.BackTest(strat)

    stats = backtest.multiprocess_testpool()
    data = {n[0]: n[2] for n in stats}
    results = []
    for ticker, value in data.items():
        df = data_reqs.get_data(ticker)
        results.append([value,df.data["chg%"].mean()])

    charting.plot_chg_v_profit(results)


def experiment_three():
    strat = MvAvgCrossover
    backtest = backtesting.BackTest(strat)

    df = data_reqs.get_data("NTLA", limit=10000)
    for _, row in df.data.iterrows():
        
                print(row["timestamp"])
                print(row["trend"])
                print(row["chg_std"])
                print(row["chg_z"])
                print(row["5_min_chg"])



# experiment_three()
# charting.plotting_trades(backtest, "NTLA")
# good_trades["outcome"] = 1
# bad_trades["outcome"] = 0
# trades = pd.concat([good_trades, bad_trades])
# correlation = trades['linear_pred'].corr(trades['outcome'])
# print(f"Correlation between prediction and outcome: {correlation}")
# trades['pred_correct'] = (
#     (trades['linear_pred'] > trades['linear_pred'].median()) == 
#     (trades['outcome'] == 1)
# )

# # Calculate accuracy
# accuracy = trades['pred_correct'].mean()

# print(f"Prediction accuracy: {accuracy * 100:.2f}%")
# charting.plotting_trades(backtest,"NTLA")


# stats = [s for s in stats if s[2] != 0]

