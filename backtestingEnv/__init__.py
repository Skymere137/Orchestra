from flask import Flask, jsonify, request
from backtestingEnv import backtesting, dataframes
from strategies import MvAvgCrossover
from strategies import ProbableCrossover
from pydantic import BaseModel
