"""Tests for event study mechanics."""
import numpy as np
import pandas as pd

from src import event_study


def _make_synthetic_prices():
    """Create deterministic prices for two tickers + market."""
    dates = pd.bdate_range("2024-01-01", "2024-12-31")
    rng = np.random.default_rng(0)
    market_ret = rng.normal(0.0005, 0.01, len(dates))
    rows = []
    for tkr in ["TEST", "SPY"]:
        if tkr == "SPY":
            ret = market_ret
        else:
            ret = 1.1 * market_ret + rng.normal(0, 0.012, len(dates))
        price = 100 * np.cumprod(1 + ret)
        for d, p, r in zip(dates, price, ret):
            rows.append({"date": d, "ticker": tkr, "adj_close": p, "return": r})
    return pd.DataFrame(rows)


def test_compute_car_returns_window():
    prices = _make_synthetic_prices()
    event_date = pd.Timestamp("2024-06-15")
    car = event_study.compute_car_for_event(prices, "TEST", event_date)
    assert car is not None
    # Should span the full event window
    assert car["tau"].min() == -5
    assert car["tau"].max() == 10
    # CAR at tau=0 should equal AR at tau=0 (cumsum starts here)
    pre_event = car[car["tau"] < 0]
    assert (pre_event["CAR"] == 0).all(), "CAR before event should be zero by convention"


def test_compute_car_handles_edge():
    """Event too close to data start should return None."""
    prices = _make_synthetic_prices()
    early = pd.Timestamp("2024-01-05")  # too close to start
    car = event_study.compute_car_for_event(prices, "TEST", early)
    assert car is None


def test_mean_car_curve():
    """Mean across multiple events should produce a 16-point curve."""
    prices = _make_synthetic_prices()
    events = pd.DataFrame([
        {"ticker": "TEST", "date": pd.Timestamp("2024-06-15"), "sector": "X",
         "direction": "negative", "event_type": "sentiment",
         "max_abs_sent": -0.8, "mean_sent": -0.5,
         "n_articles": 3, "dominant_tier": "tier_1"},
        {"ticker": "TEST", "date": pd.Timestamp("2024-08-15"), "sector": "X",
         "direction": "negative", "event_type": "sentiment",
         "max_abs_sent": -0.9, "mean_sent": -0.6,
         "n_articles": 5, "dominant_tier": "tier_1"},
    ])
    cars = event_study.compute_all_cars(prices, events)
    mean_curve = event_study.mean_car_curve(cars)
    assert len(mean_curve) == 16  # tau from -5 to +10 inclusive
    assert "mean_CAR" in mean_curve.columns
