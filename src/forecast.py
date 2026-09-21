from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn.model_selection import TimeSeriesSplit


@dataclass
class ForecastResult:
    metrics: pd.DataFrame
    forecast: pd.DataFrame


def make_features(series: pd.Series, lags: int = 3) -> tuple[pd.DataFrame, pd.Series]:
    data = pd.DataFrame({"y": series.astype(float)})
    for lag in range(1, lags + 1):
        data[f"lag_{lag}"] = data["y"].shift(lag)
    data["rolling_3"] = data["y"].shift(1).rolling(3).mean()
    data["trend"] = np.arange(len(data))
    data = data.dropna()
    X = data.drop(columns=["y"])
    y = data["y"]
    return X, y


def evaluate_models(series: pd.Series, n_splits: int = 4) -> pd.DataFrame:
    X, y = make_features(series)
    if len(X) < 10:
        raise ValueError("Not enough annual observations for a meaningful time-series backtest.")

    models = {
        "linear_regression": LinearRegression(),
        "random_forest": RandomForestRegressor(
            n_estimators=300,
            max_depth=5,
            random_state=42,
        ),
    }

    splitter = TimeSeriesSplit(n_splits=min(n_splits, len(X) - 1))
    rows = []

    for name, model in models.items():
        mae_scores, rmse_scores = [], []

        for train_idx, test_idx in splitter.split(X):
            X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
            y_train, y_test = y.iloc[train_idx], y.iloc[test_idx]

            model.fit(X_train, y_train)
            pred = model.predict(X_test)

            mae_scores.append(mean_absolute_error(y_test, pred))
            rmse_scores.append(np.sqrt(mean_squared_error(y_test, pred)))

        rows.append({
            "model": name,
            "mae_mean": float(np.mean(mae_scores)),
            "rmse_mean": float(np.mean(rmse_scores)),
            "folds": len(mae_scores),
        })

    # Transparent baseline: last observed value.
    naive_predictions = []
    naive_actuals = []
    for train_idx, test_idx in splitter.split(X):
        train_values = y.iloc[train_idx]
        test_values = y.iloc[test_idx]
        last_value = float(train_values.iloc[-1])
        naive_predictions.extend([last_value] * len(test_values))
        naive_actuals.extend(test_values.tolist())

    rows.append({
        "model": "naive_last_value",
        "mae_mean": float(mean_absolute_error(naive_actuals, naive_predictions)),
        "rmse_mean": float(np.sqrt(mean_squared_error(naive_actuals, naive_predictions))),
        "folds": splitter.get_n_splits(),
    })

    return pd.DataFrame(rows).sort_values("mae_mean").reset_index(drop=True)


def recursive_forecast(series: pd.Series, horizon: int, model_name: str) -> pd.DataFrame:
    if horizon < 1:
        raise ValueError("horizon must be >= 1")

    X, y = make_features(series)
    if model_name == "linear_regression":
        model = LinearRegression()
    elif model_name == "random_forest":
        model = RandomForestRegressor(
            n_estimators=300,
            max_depth=5,
            random_state=42,
        )
    else:
        raise ValueError(f"Unknown model: {model_name}")

    model.fit(X, y)

    history = series.dropna().astype(float).tolist()
    last_year = int(series.index.max())

    rows = []
    for step in range(1, horizon + 1):
        trend = len(history)
        features = {
            "lag_1": history[-1],
            "lag_2": history[-2],
            "lag_3": history[-3],
            "rolling_3": float(np.mean(history[-3:])),
            "trend": trend,
        }
        pred = float(model.predict(pd.DataFrame([features]))[0])
        history.append(pred)
        rows.append({
            "year": last_year + step,
            "prediction": pred,
            "model": model_name,
        })

    return pd.DataFrame(rows)


def forecast_indicator(
    df: pd.DataFrame,
    country: str,
    indicator: str = "electricity_demand",
    horizon: int = 3,
) -> ForecastResult:
    subset = df[df["country"].eq(country)][["year", indicator]].dropna().sort_values("year")
    if len(subset) < 12:
        raise ValueError(
            f"{country} has only {len(subset)} usable observations for {indicator}; need at least 12."
        )

    series = subset.set_index("year")[indicator].astype(float)

    metrics = evaluate_models(series)
    best_model = str(metrics.iloc[0]["model"])

    if best_model == "naive_last_value":
        forecast = pd.DataFrame({
            "year": [int(series.index.max()) + i for i in range(1, horizon + 1)],
            "prediction": [float(series.iloc[-1])] * horizon,
            "model": [best_model] * horizon,
        })
    else:
        forecast = recursive_forecast(series, horizon=horizon, model_name=best_model)

    forecast.insert(0, "country", country)
    forecast.insert(1, "indicator", indicator)

    return ForecastResult(metrics=metrics, forecast=forecast)
