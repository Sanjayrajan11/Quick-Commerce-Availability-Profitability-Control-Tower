"""Chronological model selection with untouched final holdout."""

import numpy as np
import pandas as pd

MODELS = ["Naive", "Moving average", "Exponential smoothing", "Seasonal naive"]


def predict(history, horizon, model):
    y = np.asarray(history, dtype=float)
    if horizon < 1 or len(y) == 0 or not np.isfinite(y).all() or (y < 0).any():
        raise ValueError(
            "Forecast needs finite non-negative history and positive horizon"
        )
    if model == "Naive":
        return np.repeat(y[-1], horizon)
    if model == "Moving average":
        return np.repeat(y[-7:].mean(), horizon)
    if model == "Seasonal naive":
        return np.resize(y[-7:], horizon)
    if model == "Exponential smoothing":
        level = y[0]
        for value in y[1:]:
            level = 0.3 * value + 0.7 * level
        return np.repeat(level, horizon)
    raise ValueError("Unknown model")


def evaluate(actual, predicted):
    y, p = np.asarray(actual), np.asarray(predicted)
    if len(y) == 0 or y.shape != p.shape:
        raise ValueError("Aligned nonempty evaluation required")
    error = p - y
    return {
        "mae": float(np.abs(error).mean()),
        "rmse": float(np.sqrt((error**2).mean())),
        "wape": float(np.abs(error).sum() / np.abs(y).sum())
        if np.abs(y).sum()
        else 0.0,
        "bias_units": float(error.mean()),
        "wape_defined": bool(np.abs(y).sum()),
    }


def forecast(series: pd.Series, horizon=14):
    y = series.astype(float)
    if len(y) < 42:
        raise ValueError("At least 42 daily observations required")
    train, validation, test = y.iloc[:-28], y.iloc[-28:-14], y.iloc[-14:]
    scores = {
        model: evaluate(validation, predict(train, 14, model))["mae"]
        for model in MODELS
    }
    chosen = min(scores, key=scores.get)
    metrics = []
    backtests = []
    for model in MODELS:
        pred = predict(y.iloc[:-14], 14, model)
        metrics.append(
            {
                "model": model,
                "selected": model == chosen,
                "validation_mae": scores[model],
                **evaluate(test, pred),
                "train_end": str(train.index[-1]),
                "validation_end": str(validation.index[-1]),
                "test_start": str(test.index[0]),
                "test_end": str(test.index[-1]),
            }
        )
        backtests.append(
            pd.DataFrame(
                {
                    "date": test.index,
                    "actual_units": test.values,
                    "forecast_units": pred,
                    "model": model,
                }
            )
        )
    residual = np.abs(validation.to_numpy() - predict(train, 14, chosen))
    radius = float(np.quantile(residual, 0.9))
    future = predict(y, horizon, chosen)
    out = pd.DataFrame(
        {
            "date": pd.date_range(
                pd.Timestamp(y.index[-1]) + pd.Timedelta(days=1), periods=horizon
            ),
            "forecast_units": future,
            "lower_units": np.maximum(0, future - radius),
            "upper_units": future + radius,
            "model": chosen,
        }
    )
    return out, pd.DataFrame(metrics), pd.concat(backtests, ignore_index=True)


def all_forecasts(items, dates):
    outputs = []
    metrics = []
    backtests = []
    for dimension in ["total", "store_id", "category_id", "product_id"]:
        groups = [("All", items)] if dimension == "total" else items.groupby(dimension)
        for key, group in groups:
            series = (
                group.groupby("date")
                .quantity_ordered.sum()
                .reindex(pd.Index(dates).astype(str), fill_value=0)
            )
            series.index = pd.to_datetime(series.index)
            future, score, backtest = forecast(series)
            for frame in [future, score, backtest]:
                frame["dimension"] = dimension
                frame["entity"] = str(key)
            outputs.append(future)
            metrics.append(score)
            backtests.append(backtest)
    return (
        pd.concat(outputs, ignore_index=True),
        pd.concat(metrics, ignore_index=True),
        pd.concat(backtests, ignore_index=True),
    )
