import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from backtestingEnv import backtesting
from strategies import MvAvgCrossover

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
        plt.scatter(
            good_df['timestamp'],
            good_df['linear_pred'],
            color='yellow',
            s=40,
            label="Good Trades",
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
        plt.scatter(
            good_df['timestamp'],
            good_df['linear_pred'],
            color='yellow',
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


def plot_marketcap_histogram(data: list, bins: int = 50) -> None:
    market_caps = []
    for entry in data:
        for symbol, fields in entry.items():
            value_str = fields["MarketCap"]["value"]
            value = float(value_str.replace(",", ""))
            market_caps.append(value)

    caps_billions = [v / 1e9 for v in market_caps]

    plt.figure(figsize=(12, 6))
    plt.hist(caps_billions, bins=bins, edgecolor="black", color="steelblue")
    plt.xlabel("Market Cap (Billions USD)")
    plt.ylabel("Number of Stocks")
    plt.title("Market Cap Distribution")
    plt.tight_layout()
    plt.show()

def plot_marketcap_vs_yield(entries: list) -> None:
    market_caps = []
    yields = []
    tickers = []

    for entry in entries:
        for symbol, fields in entry.items():
            try:
                mc_str = fields["MarketCap"]["value"]
                if mc_str == "N/A":
                    continue
                market_cap = float(mc_str.replace(",", ""))
                profit = float(fields["Profit"]["value"])
                if market_cap <= 0:
                    continue

                market_caps.append(market_cap / 1e9)
                yields.append(profit)
                tickers.append(symbol)
            except (KeyError, ValueError):
                continue

    plt.figure(figsize=(12, 6))
    plt.scatter(market_caps, yields, alpha=0.6, edgecolors="black", color="steelblue")
    plt.axhline(0, color="red", linewidth=0.8, linestyle="--")
    plt.xscale("log")
    plt.xlabel("Market Cap (Billions USD, log scale)")
    plt.ylabel("Profit")
    plt.title("Profit vs Market Cap")

    for i, ticker in enumerate(tickers):
        plt.annotate(ticker, (market_caps[i], yields[i]), fontsize=7, alpha=0.7)

    plt.tight_layout()
    plt.show()

def plot_chg_v_profit(data: list) -> None:
    profits = []
    chg = []

    for i in data:
        if i[0] is None or i[1] is None or i[0] <= 0:
            continue
        profits.append(i[0])
        chg.append(float(i[1]))

    profits = np.array(profits)
    chg = np.array(chg)

    plt.figure(figsize=(10, 10))
    plt.scatter(chg, profits, alpha=0.6, edgecolors="black", color="steelblue")
    plt.axhline(0, color="red", linewidth=0.8, linestyle="--")
    plt.xlabel("chg")
    plt.ylabel("Profit")
    plt.title("Profit vs chg%")
    plt.tight_layout()
    plt.show()