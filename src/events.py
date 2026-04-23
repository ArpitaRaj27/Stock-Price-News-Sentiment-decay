"""Event identification.

An "event" is a day where something notable happened for a ticker.
We use two definitions (applied independently, then unioned):

  1. Sentiment threshold: on a given day, the max |compound sentiment| across
     articles for that ticker exceeds SENTIMENT_THRESHOLD.
  2. Volume spike: number of articles on a day > (mean + VOLUME_SPIKE_SIGMA * std)
     of a rolling 30-day window for that ticker.

Each event carries: ticker, date, sentiment, dominant source tier, type.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from src import config


def aggregate_news_daily(scored_news: pd.DataFrame) -> pd.DataFrame:
    """Collapse intraday articles to daily-level features per ticker."""
    g = scored_news.groupby(["ticker", "date"])
    daily = g.agg(
        n_articles=("headline", "count"),
        mean_sent=("sent_compound", "mean"),
        max_abs_sent=("sent_compound", lambda x: x.loc[x.abs().idxmax()]),
        dominant_tier=("source_tier", lambda x: x.mode().iat[0] if len(x.mode()) else "unknown"),
    ).reset_index()
    return daily


def identify_events(
    daily_news: pd.DataFrame,
    sentiment_threshold: float = config.SENTIMENT_THRESHOLD,
    volume_sigma: float = config.VOLUME_SPIKE_SIGMA,
    rolling_window: int = config.VOLUME_ROLLING_WINDOW,
) -> pd.DataFrame:
    """Return DataFrame of events. One row per ticker-event-day."""
    df = daily_news.sort_values(["ticker", "date"]).copy()

    # Rolling mean + std of article volume, per ticker
    df["vol_mean"] = df.groupby("ticker")["n_articles"].transform(
        lambda s: s.rolling(rolling_window, min_periods=5).mean()
    )
    df["vol_std"] = df.groupby("ticker")["n_articles"].transform(
        lambda s: s.rolling(rolling_window, min_periods=5).std()
    )
    df["vol_spike"] = df["n_articles"] > (df["vol_mean"] + volume_sigma * df["vol_std"])
    df["sent_spike"] = df["max_abs_sent"].abs() >= sentiment_threshold

    df["is_event"] = df["vol_spike"] | df["sent_spike"]
    events = df[df["is_event"]].copy()

    # Classify event direction
    events["direction"] = np.where(events["max_abs_sent"] > 0, "positive", "negative")

    # Add sector
    sector_map = config.ticker_to_sector()
    events["sector"] = events["ticker"].map(sector_map)

    # Event type (for diagnostics)
    events["event_type"] = np.where(
        events["sent_spike"] & events["vol_spike"], "both",
        np.where(events["sent_spike"], "sentiment", "volume")
    )

    keep_cols = [
        "ticker", "date", "sector", "direction", "event_type",
        "max_abs_sent", "mean_sent", "n_articles", "dominant_tier",
    ]
    return events[keep_cols].reset_index(drop=True)
