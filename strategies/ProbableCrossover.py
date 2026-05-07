import numpy as np
# from backtestingEnv.dataframes import EstablishDataframe

class ProbabilityCrossover:
    def __init__(self, min_r):
        self.name = "Probability Crossover"

    def make_trade_params(self, df, row, levels, min_r=10):
        entry = None
        # print(df.loc[row, "prob_up"], df.loc[row, "sma10"], df.loc[row, "sma50"], df.loc[row, "z"])
        if df.loc[row, "prob_up"] > .95:
            if df.loc[row, "z"] < .25:
                entry = df.loc[row, "close"]
                stop = df.loc[row, "sma10"]
                target = ((df.loc[row, "close"] - df.loc[row, "sma10"]) * min_r) + df.loc[row, "sma50"]
        
        if entry:
            print(entry, stop, target)
            return entry, stop, target
        else:
            return np.nan, np.nan, np.nan
                

# df = EstablishDataframe("backtestingEnv/one_min_s/METC.json")
# crossover = ProbableCrossover()

# for ei in df.data.index:

#     crossover.make_trade_params(df, ei)