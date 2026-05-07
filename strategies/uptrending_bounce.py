import numpy as np
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class UptrendingBounce:
    def __init__(self, min_r=10):
        self.min_r = min_r
        self.name = "Uptrening Bounce"
        
    def fibonacci(self, zero, one):
        fibonacci_levels = [0, .236, .382, .5, .618, .786, 1, 1.618, 2.618]
            
        high = max(zero, one)
        low = min(zero, one)
        diff = high - low
        nums = [low + (num * diff) for num in fibonacci_levels]
        return nums
    
    def make_trade_params(self, row, levels):
        if row["price_z"] == 0:
            return np.nan, np.nan, np.nan
        # logger.info(row["timestamp"])
        # logger.info(type(row["timestamp"]))
        levels = [level for level in levels if level["touches"][0] < row.name]
        levels_above = [level for level in levels if level["price"] > row["close"]]
        if not levels_above:
            return np.nan, np.nan, np.nan
            
        nearest_res = min(levels_above, key=lambda x: x["price"])

        if row["close"] > row["vwap"]:
            for level in levels:
                if (row["open"] - level["price"]) <= (row["price_std"]):
                    if row["close"] > row["open"]:
                        if row["price_z"] > 1:
                            fib = self.fibonacci(row["close"], nearest_res["price"])
                            entry  = row["close"]
                            stop  = level["price"] - row["price_std"]
                            target = fib[7]
                            risk = (entry - stop)
                            reward = target - entry
                            if (reward / risk) < 3:
                                    # print("Not enough reward")
                                return np.nan, np.nan, np.nan
                            if ((risk / row["close"]) * 100) > 2:
                                    # print("Too much risk")
                                return np.nan, np.nan, np.nan
                            # print(row.name)
                            # print((reward / risk) < 2)
                            # print(f"entry: {entry:.4f}, stop: {stop:.4f}, target: {target:.4f}")
                            # print(f"risk: {risk:.4f}, reward: {reward:.4f}, rr: {reward/risk:.2f}")
                            # print("RETURNING VALID TRADE")
                            return float(entry), float(level["price"] - row["price_std"]), float(target)
        return np.nan, np.nan, np.nan