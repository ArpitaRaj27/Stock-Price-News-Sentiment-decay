"""Tests for data_loader."""
import pandas as pd
from src import data_loader, config


def test_demo_prices_shape():
    tickers = ["AAPL", "MSFT"]
    df = data_loader.load_prices_demo(tickers, start="2024-01-01", end="2024-03-31")
    assert set(df["ticker"].unique()) >= set(tickers)
    assert "return" in df.columns
    assert "adj_close" in df.columns
    # First return per ticker should be NaN
    firsts = df.groupby("ticker").head(1)
    assert firsts["return"].isna().all()


def test_demo_news_shape():
    tickers = ["AAPL", "JPM"]
    df = data_loader.load_news_demo(tickers, start="2024-01-01", end="2024-03-31")
    assert len(df) > 0
    assert set(df.columns) >= {"ticker", "datetime", "headline", "source", "source_tier", "true_sentiment"}
    assert df["source_tier"].isin(["tier_1", "tier_2", "tier_3"]).all()


def test_classify_source():
    assert config.classify_source("Reuters") == "tier_1"
    assert config.classify_source("Bloomberg News") == "tier_1"
    assert config.classify_source("Seeking Alpha") == "tier_2"
    assert config.classify_source("Yahoo Finance") == "tier_3"
    assert config.classify_source("Some Random Blog") == "unknown"


def test_universe():
    tickers = config.all_tickers()
    assert len(tickers) == 30
    sector_map = config.ticker_to_sector()
    assert sector_map["AAPL"] == "Technology"
    assert sector_map["JPM"] == "Financials"
