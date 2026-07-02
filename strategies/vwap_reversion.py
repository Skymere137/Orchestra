from datetime import time
import pandas as pd

class VwapReversion:
    def __init__(self):
        self.preserve_state = None

        self.start = time(6, 30)
        self.end = time(13, 0)

        self.projected_R = None
        self.entry_vwap = None
        self.exit_vwap = None
        self.z_on_exit = None

        self.add_on_entry = {"projected_R": self.projected_R, "entry_vwap": self.entry_vwap}
        self.add_on_exits = {"exit_vwap": self.exit_vwap, "z_on_exit": self.z_on_exit}

    def reverse_z_index(self, row, index=None):
        if index:
            return (index * row["vwap_std"]) + row["vwap"]
        return (row["z_vwap"] * row["vwap_std"]) + row["vwap"]
    
    def is_in_range(self, timestamp):
        t = pd.Timestamp(timestamp).time()
        t = (
            pd.Timestamp(timestamp)
            .tz_localize("UTC")
            .tz_convert("America/Los_Angeles")
            .time()
        )
        return self.start <= t <= self.end

    def make_trade_params(self, row, min_r):
        def entry(row):
            if self.is_in_range(row["timestamp"]):
                if row["z_vwap"] < -1.8:
                    risk = self.reverse_z_index(row, index = -5) - row["close"]
                    reward = row["vwap"] - row["close"]
                    
                    if risk <= 0 or reward <= 0:
                        return False
                    self.add_on_entry["projected_R"] = (reward / risk)
                    self.add_on_entry["entry_vwap"] = row["vwap"]
                    self.add_on_entry["angle"] = row["angle"]
                        
                        # print(f"risk: {risk},\nReward: {reward}\nR: {(reward / risk)}")
                    return True
            return False
        
        def stop(row):
            if not self.is_in_range(row["timestamp"]):
                return True
            if row["z_vwap"] < -5:
                self.add_on_exits["exit_vwap"] = row["vwap"]
                self.add_on_exits["z_on_exit"] = row["z_vwap"]
                return True
            return False

        def target(row):
            if row["z_vwap"] > 0:
                self.add_on_exits["exit_vwap"] = row["vwap"]
                self.add_on_exits["z_on_exit"] = row["z_vwap"]
                return True
            return False
        
        return entry, stop, target