import os
import logging
from flask import Flask, jsonify, request
from backtestingEnv import backtesting, dataframes
from strategies import MvAvgCrossover
from strategies import ProbableCrossover
from strategies import UptrendingBounce
from annie_reqs import data_reqs, portfolio_reqs
from pydantic import BaseModel

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

class Model(BaseModel):
    strategy: str
    ticker: str
    path: str
    min_r: int
    min_trade: float
    time_range: int

current_model = {
    "strategy": MvAvgCrossover,
    "ticker": "AAMI",
    "path": r"one_min_s",
    "min_r": 5,
    "min_trade": 0.1,
    "time_range": 0
}

watchlist = []

strategies = {
    "Moving Average Crossover": MvAvgCrossover,
    "Balance of Probability": ProbableCrossover.ProbabilityCrossover,
    "Uptrending Bounce": UptrendingBounce
}

@app.route("/")
def set_env():
    strat = current_model["strategy"](current_model["min_r"])
    if not strat:
        return "No strategy selected please change model to the desired strategy"
    return strat.name

@app.route("/change_strat", methods=["POST"])
def change_strat():
    data = request.get_json()
    model = Model(**data)
    current_model["strategy"] = strategies[model.strategy]
    current_model["ticker"] = model.ticker
    current_model["path"] = model.path
    current_model["min_r"] = model.min_r
    current_model["min_trade"] = model.min_trade
    current_model["time_range"] = model.time_range
    return jsonify({"status": "ok", "model": model.model_dump()})

@app.route("/plt_trades", methods=["GET"])
def plt_trades():
    try:

        backtest = backtesting.BackTest(current_model["strategy"], current_model["path"])

        stats = backtest.plotting_trades(current_model["ticker"])
        
        return jsonify(make_json_safe(stats))
    
    except Exception as e:
        return jsonify({
            "error": str(e),
            "endpoint": "/plt_trades"
        }), 500

@app.route("/mono_test", methods=["GET"])
def mono_test():
    try:
        backtest = backtesting.BackTest(current_model["strategy"], current_model["path"])
        stats = backtest.run_strat(current_model["ticker"], current_model["min_trade"], current_model["time_range"])
        
        return make_json_safe(stats)
    except Exception as e:
        return jsonify({
            "error": str(e),
            "endpoint": "/mono_test"
        }), 500
    
@app.route("/backtest_results", methods=["GET"])
def backtest_results():
    backtest = backtesting.BackTest(current_model["strategy"], current_model["path"])
    results = backtest.multiprocess_testpool()
    watchlist.append(results)
    return results

@app.route("/dataframe_test", methods=["GET"])
def test_dataframes():
    dfs = dataframes.EstablishDataframe("backtestingEnv/one_min_l/AAPL.json")
    return make_json_safe(dfs.data)

@app.route("/compareTimeMargins", methods=["GET"])
def compare_time_margins():
    backtest = backtesting.BackTest(current_model["strategy"], current_model["path"])
    results = backtest.compare_temp_margins(current_model["ticker"])
    return make_json_safe(results)


@app.route("/testing", methods=["GET"])
def testing():
    data = data_reqs.get_data()
    logger.info(data)
    return make_json_safe(data)

def make_json_safe(obj):
    if isinstance(obj, dict):
        return {k: make_json_safe(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [make_json_safe(v) for v in obj]
    elif hasattr(obj, "__dict__"):
        return str(obj)
    elif isinstance(obj, (int, float, str, bool)) or obj is None:
        return obj
    else:
        return str(obj)
    

if __name__ == "__main__":
    app.run()