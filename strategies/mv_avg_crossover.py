import numpy as np 

class MvAvgCrossover:
    def __init__(self, min_r):
        self.R = min_r
        self.name = "Moving Average Crossover"

    def fibonacci(self, zero, one):
        fibonacci_levels = [0, .236, .382, .5, .618, .786, 1, 1.618, 2.618]
            
        high = max(zero, one)
        low = min(zero, one)
        diff = high - low
        nums = [low + (num * diff) for num in fibonacci_levels]
        return nums

    def make_trade_params(self, row, min_rr=1.5):
        if row["sma10"] > row["sma50"]:
            fib = self.fibonacci(row["sma50"], row["close"])
            
            entry = fib[1]
            stop = row["sma50"]
            target = fib[-1]           

            risk = entry - stop
            reward = target - entry
            rr = reward / risk if risk != 0 else 0

            if rr >= min_rr:
                return entry, stop, target
            
        return np.nan, np.nan, np.nan
