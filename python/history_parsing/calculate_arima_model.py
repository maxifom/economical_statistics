import json
from datetime import datetime

import math
import pandas as pd
import warnings

from models import Company

import matplotlib.pyplot as plt

from statsmodels.tsa.arima_model import ARIMA

import numpy as np

if __name__ == '__main__':
    companies = Company.select()
    for c in companies:
        df = pd.read_csv(f"./../../data/all_params/{c.ticker}.csv")
        df["next_close"] = df.close.shift(-1)
        df.dropna(inplace=True)
        t = datetime(2016, 1, 1, 0, 0, 0, 0)
        df.date = pd.to_datetime(df.date)
        df = df[df.date >= t]
        df.reset_index(inplace=True, drop=True)
        items_count = len(df)
        splitCount = int(items_count * 0.8)
        train_data = df[:splitCount]
        test_data = df[splitCount:]
        train_dataset = [x for x in train_data["close"]]
        test_dataset = [x for x in test_data["close"]]
        warnings.filterwarnings('ignore')
        min = 1e9
        min_param = (0, 1, 5)
        predictions = []
        model_fit = None
        for t in test_dataset:
            model_fit = ARIMA(train_dataset, order=min_param).fit(disp=False)
            predictions.append(model_fit.forecast(steps=1)[0][0])
            train_dataset.append(t)
        test_data.reset_index(inplace=True)
        md = {"params": model_fit.params.tolist(), "aic": model_fit.aic, "bic": model_fit.bic}

        df_copy = test_data.copy()
        df_copy.set_index(keys=["date"], inplace=True)
        df_copy = df_copy.rolling(min_periods=1, window=50, on="close").mean()
        df_copy.reset_index(inplace=True)
        test_data["mean_close"] = df_copy.close

        test_data["prediction"] = predictions
        test_data["error"] = (test_data["prediction"] - test_data["close"]) ** 2
        test_val_loss = math.sqrt(test_data.error.mean())
        test_val_loss_percent = test_val_loss / test_data.close.mean()

        md["test_val_loss"] = test_val_loss
        md["test_val_loss_percent"] = test_val_loss_percent
        test_data["prediction_trend"] = test_data["prediction"] > test_data["close"]
        test_data["actual_trend"] = test_data["next_close"] > test_data["close"]
        test_data["is_accurate"] = test_data["prediction_trend"] == test_data["actual_trend"]
        test_data["acc_cum_sum"] = test_data.is_accurate.cumsum()
        test_data["acc"] = (test_data["acc_cum_sum"] / (test_data.index + 1)) * 100
        test_data["val_loss"] = np.sqrt(test_data.error.cumsum() / (test_data.index + 1))
        test_data["val_loss_pct"] = ((np.sqrt(
            test_data.error.cumsum() / (test_data.index + 1))) / test_data.mean_close) * 100
        test_acc = test_data.is_accurate.sum() / test_data.is_accurate.count()
        md["test_acc"] = test_acc
        c.arima_model = json.dumps(md)
        c.save()
        plt.figure(figsize=(12.8, 7.2))
        plt.plot(test_data.date, test_data.close, label="Actual")
        plt.plot(test_data.date, test_data.prediction, label="Prediction", alpha=0.8)
        plt.xlabel("Date")
        plt.ylabel("Price, RUB")
        plt.title(c.name)
        plt.legend()
        plt.savefig(f"./../../data/plots/arima/price/{c.ticker}.png", format="png")
        plt.clf()

        plt.figure(figsize=(12.8, 7.2))
        plt.plot(test_data.date[5:], test_data.acc[5:], label="Test accuracy")
        plt.xlabel("Date")
        plt.ylabel("Test accuracy, %")
        plt.title(c.name)
        plt.legend()
        plt.savefig(f"./../../data/plots/arima/acc/{c.ticker}.png", format="png")
        plt.clf()

        plt.figure(figsize=(12.8, 7.2))
        plt.plot(test_data.date, test_data.val_loss, label="Test Value loss")

        plt.xlabel("Date")
        plt.ylabel("Test value loss")
        plt.title(c.name)
        plt.legend()
        plt.savefig(f"./../../data/plots/arima/val_loss/{c.ticker}.png", format="png")
        plt.clf()

        plt.figure(figsize=(12.8, 7.2))
        plt.plot(test_data.date, test_data.val_loss_pct, label="Test Value loss pct")

        plt.xlabel("Date")
        plt.ylabel("Test value loss")
        plt.title(c.name)
        plt.legend()
        plt.savefig(f"./../../data/plots/arima/val_loss_pct/{c.ticker}.png", format="png")
        plt.clf()
        test_data.to_csv(f"./../../data/graph_data/arima/{c.ticker}.csv", index=False)
        test_data[["date", "acc"]][5:].to_csv(f"./../../data/graph_data/arima/acc_{c.ticker}.csv", index=False)
        test_data[["date", "val_loss"]].to_csv(f"./../../data/graph_data/arima/val_loss_{c.ticker}.csv", index=False)
        test_data[["date", "val_loss_pct"]].to_csv(f"./../../data/graph_data/arima/val_loss_pct_{c.ticker}.csv",
                                                   index=False)
