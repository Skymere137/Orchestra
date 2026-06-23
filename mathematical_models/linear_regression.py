import matplotlib.pyplot as plt
import numpy as np


class LinearRegression:
    def __init__(self):
        self.slope = None
        self.intercept = None
        self.r_squared = None
    
    def fit(self, x, y):
        try:
            x = np.array(x, dtype=float)
            y = np.array(y, dtype=float)
        except:
            print(y)
        x_mean = x.mean()
        y_mean = y.mean()

        numerator = np.sum((x - x_mean) * (y - y_mean))
        denominator = np.sum((x - x_mean)**2)

        self.slope = numerator / denominator

        self.intercept = y_mean - self.slope * x_mean

        y_pred = self.predict(x)
        ss_total = np.sum((y - y_mean)**2)
        ss_residual = np.sum((y - y_pred)**2)
        self.r_squared = 1 - (ss_residual / ss_total)

        return self

    def predict(self, x):
        return self.slope * x + self.intercept

    def plot(self, x, y):
        plt.figure(figsize=(10,6))
        plt.scatter(x, y, color='blue', label='Data points')
        plt.xlim(min(x), max(x))
        plt.show()