import numpy as np 

class MvAvgCrossover:
    def __init__(self):
        self.name = "Moving Average Crossover"
        self.preserve_state = None

        self.add_on_entry = {}
        self.add_on_exits = {}


    def fibonacci(self, zero, one):
        fibonacci_levels = [0, .236, .382, .5, .618, .786, 1, 1.618, 2.618]
            
        high = max(zero, one)
        low = min(zero, one)
        diff = high - low
        nums = [low + (num * diff) for num in fibonacci_levels]
        return nums

    def make_trade_params(self, row, min_r):
        def entry(row):
            if row["sma10"] > row["sma50"] and row["close"] > row["sma50"]:
                # use sma10 as the "high" anchor instead of close
                # so fib levels are stable and meaningful
                fib = self.fibonacci(row["sma50"], row["sma10"])
                risk = fib[1] - row["sma50"]
                reward = fib[-1] - fib[1]
                if risk <= 0:
                    return False
                rr = reward / risk
                if row["close"] <= fib[1] and rr >= min_r:
                    self.preserve_state = fib
                    self.add_on_entry["projected_R"] = (reward / risk)
                    self.add_on_entry["entry_vwap"] = row["vwap"]
                    self.add_on_entry["angle"] = row["angle"]
                    return True
            return False

        def stop(row):
            if row["sma10"] < row["sma50"]:
                self.preserve_state = None
                self.add_on_exits["exit_vwap"] = row["vwap"]
                self.add_on_exits["z_on_exit"] = row["z_vwap"]
                return True
            return False

        def target(row):
            if self.preserve_state and row["close"] >= self.preserve_state[-1]:
                self.preserve_state = None
                self.add_on_exits["exit_vwap"] = row["vwap"]
                self.add_on_exits["z_on_exit"] = row["z_vwap"]
                return True
            return False

        return entry, stop, target
            
        
