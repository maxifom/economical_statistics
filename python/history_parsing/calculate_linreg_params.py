"""
    Calculates linreg parameters, accuracy and value losses and draws graphs
"""

import json
from datetime import datetime

import math
import matplotlib.pyplot as plt
import statsmodels.api as sm
import pandas as pd
from models import Company

import numpy as np


def predict(x, params):
    prediction = params["const"]
    for p in params.keys()[1:]:
        prediction += x[p] * params[p]
    return pd.Series(prediction)


def calculate_linreg_coef_and_pvalues_statsmodels():
    companies = Company.select()
    for c in companies:
        df = pd.read_csv(f"./../../data/all_params/{c.ticker}.csv")
        df["next_close"] = df.close.shift(-1)
        df.dropna(inplace=True)
        t = datetime(2016, 1, 1, 0, 0, 0, 0)
        df.date = pd.to_datetime(df.date)
        df = df[df.date >= t]
        df.reset_index(inplace=True, drop=True)

        x_80_pct = int(df.shape[0] * 0.80)
        x_train = df.iloc[:x_80_pct, 4:-1]
        y_train = df.iloc[:x_80_pct, -1]
        x_test = df.iloc[:, 4:-1]
        x_ = sm.add_constant(x_train)
        smm = sm.OLS(y_train, x_)
        model = smm.fit()
        md = {"rsquared": model.rsquared, "params": model.params.to_dict(), "pvalues": model.pvalues.to_dict(),
              "tvalues": model.tvalues.to_dict(), "fvalue": model.fvalue, "f_pvalue": model.f_pvalue, "aic": model.aic,
              "bic": model.bic}
        df_copy = df.copy()
        df_copy.set_index(keys=["date"], inplace=True)
        df_copy = df_copy.rolling(min_periods=1, window=50, on="close").mean()
        df_copy.reset_index(inplace=True)
        df["mean_close"] = df_copy.close
        df["prediction"] = x_test.apply(predict, axis=1, args=(model.params,))
        df["error"] = (df["prediction"] - df["next_close"]) ** 2
        train_val_loss = math.sqrt(df.iloc[:x_80_pct, :].error.mean())
        train_val_loss_percent = train_val_loss / df.iloc[:x_80_pct, :].close.mean()
        test_val_loss = math.sqrt(df.iloc[x_80_pct:, :].error.mean())
        test_val_loss_percent = test_val_loss / df.iloc[x_80_pct:, :].close.mean()
        md["train_val_loss"] = train_val_loss
        md["test_val_loss"] = test_val_loss
        md["train_val_loss_percent"] = train_val_loss_percent
        md["test_val_loss_percent"] = test_val_loss_percent
        df["prediction_trend"] = df["prediction"] > df["close"]
        df["actual_trend"] = df["next_close"] > df["close"]
        df["is_accurate"] = df["prediction_trend"] == df["actual_trend"]

        df["acc_cum_sum"] = df.is_accurate.cumsum()

        df["acc"] = (df["acc_cum_sum"] / (df.index + 1)) * 100
        df["val_loss"] = np.sqrt(df.error.cumsum() / (df.index + 1))
        df["val_loss_pct"] = ((np.sqrt(df.error.cumsum() / (df.index + 1))) / df.mean_close) * 100

        train_acc = df.iloc[:x_80_pct, :].is_accurate.sum() / df.iloc[:x_80_pct, :].is_accurate.count()
        test_acc = df.iloc[x_80_pct:, :].is_accurate.sum() / df.iloc[x_80_pct:, :].is_accurate.count()
        md["train_acc"] = train_acc
        md["test_acc"] = test_acc
        c.linear_model = json.dumps(md)
        c.save()

        # Price graph with predictions
        plt.figure(figsize=(12.8, 7.2))
        plt.plot(df.date, df.next_close, label="Actual")
        plt.plot(df.date, df.prediction, label="Prediction", alpha=0.8)
        x_80_pct_date = datetime.fromtimestamp(
            df.iloc[x_80_pct:x_80_pct + 1, :].date.item() * 1e-9)  # convert to seconds
        plt.axvline(x=x_80_pct_date, color="#008000")
        plt.xlabel("Date")
        plt.ylabel("Price, RUB")
        plt.title(c.name)
        plt.legend()
        plt.savefig(f"./../../data/plots/price/{c.ticker}.png", format="png")
        plt.clf()
        # Accuracy
        plt.figure(figsize=(12.8, 7.2))
        # Don't calc first 5 because of scale issues when acc = 100%
        plt.plot(df.date[5:], df.acc[5:], label="Accuracy")
        # plt.plot(df.date, df.prediction, label="Prediction", alpha=0.8)
        x_80_pct_date = datetime.fromtimestamp(
            df.iloc[x_80_pct:x_80_pct + 1, :].date.item() * 1e-9)  # convert to seconds
        plt.axvline(x=x_80_pct_date, color="#008000")
        plt.xlabel("Date")
        plt.ylabel("Accuracy, %")
        plt.title(c.name)
        plt.legend()
        plt.savefig(f"./../../data/plots/acc/{c.ticker}.png", format="png")
        plt.clf()
        # Value loss
        plt.figure(figsize=(12.8, 7.2))
        plt.plot(df.date, df.val_loss, label="Value Loss")
        # plt.plot(df.date, df.prediction, label="Prediction", alpha=0.8)
        x_80_pct_date = datetime.fromtimestamp(
            df.iloc[x_80_pct:x_80_pct + 1, :].date.item() * 1e-9)  # convert to seconds
        plt.axvline(x=x_80_pct_date, color="#008000")
        plt.xlabel("Date")
        plt.ylabel("Value Loss")
        plt.title(c.name)
        plt.legend()
        plt.savefig(f"./../../data/plots/val_loss/{c.ticker}.png", format="png")
        plt.clf()
        # Value loss percentage of mean price
        plt.figure(figsize=(12.8, 7.2))
        plt.plot(df.date, df.val_loss_pct, label="Value Loss % of mean price")
        # plt.plot(df.date, df.prediction, label="Prediction", alpha=0.8)
        x_80_pct_date = datetime.fromtimestamp(
            df.iloc[x_80_pct:x_80_pct + 1, :].date.item() * 1e-9)  # convert to seconds
        plt.axvline(x=x_80_pct_date, color="#008000")
        plt.xlabel("Date")
        plt.ylabel("Value Loss, %")
        plt.title(c.name)
        plt.legend()
        plt.savefig(f"./../../data/plots/val_loss_pct/{c.ticker}.png", format="png")
        plt.clf()
        df.to_csv(f"./../../data/graph_data/linreg/{c.ticker}.csv", index=False)


if __name__ == '__main__':
    calculate_linreg_coef_and_pvalues_statsmodels()
