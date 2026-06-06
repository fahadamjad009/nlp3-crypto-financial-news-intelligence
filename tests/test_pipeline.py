"""
Unit tests for NLP3 crypto news pipeline.
Run: python -m pytest tests/ -v
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import pytest
import pandas as pd
from classifier import rule_based_classify, classify_dataframe_fast, LABELS, LABEL_COLORS, LABEL_EMOJIS
from trend_detector import get_label_distribution, get_market_sentiment_score, get_ticker_distribution
from news_fetcher import tag_tickers, tag_exchanges, tag_macro, generate_sample_news


def test_rule_based_classify_returns_keys():
    result = rule_based_classify("Bitcoin surges to record high on ETF approval")
    assert "primary_label" in result
    assert "active_labels" in result
    assert "scores" in result
    assert "emoji" in result


def test_bullish_classification():
    result = rule_based_classify("Bitcoin surges past $70,000 as institutional demand hits record highs")
    assert result["primary_label"] == "bullish"


def test_bearish_classification():
    result = rule_based_classify("Crypto markets crash 15 percent after surprise CPI inflation data")
    assert result["primary_label"] in ["bearish", "macro"]


def test_regulatory_classification():
    result = rule_based_classify("SEC approves spot Ethereum ETF applications from BlackRock")
    assert result["primary_label"] in ["regulatory", "bullish", "macro"]


def test_technical_classification():
    result = rule_based_classify("Solana network processes 65,000 transactions per second in stress test")
    assert result["primary_label"] == "technical"


def test_scores_sum_not_zero():
    result = rule_based_classify("Ethereum gas fees drop 80 percent following Dencun upgrade")
    total = sum(result["scores"].values())
    assert total > 0


def test_tag_tickers_btc():
    tickers = tag_tickers("Bitcoin surges past $70,000 as demand hits record highs")
    assert "BTC" in tickers


def test_tag_tickers_eth():
    tickers = tag_tickers("Ethereum ETF approved by SEC")
    assert "ETH" in tickers


def test_generate_sample_news():
    articles = generate_sample_news()
    assert len(articles) >= 10
    assert "title" in articles[0]
    assert "source" in articles[0]


def test_classify_dataframe_fast():
    df = pd.DataFrame({
        "title": [
            "Bitcoin surges to record high",
            "SEC cracks down on crypto exchanges",
            "Ethereum network upgrade successful",
        ]
    })
    result = classify_dataframe_fast(df)
    assert "primary_label" in result.columns
    assert "score_bullish" in result.columns
    assert len(result) == 3


def test_market_sentiment_score():
    df = pd.DataFrame({
        "primary_label": ["bullish","bullish","bullish","bearish","macro"]
    })
    score = get_market_sentiment_score(df)
    assert 0 <= score <= 100
    assert score > 50