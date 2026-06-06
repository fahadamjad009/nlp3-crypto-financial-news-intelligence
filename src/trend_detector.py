"""
Crypto news trend detection pipeline.
Detects trending tickers, topics, sentiment shifts over time.
"""

import pandas as pd
import numpy as np
from collections import Counter
from datetime import datetime
import os
import ast


CRYPTO_TICKERS = {
    "BTC": "Bitcoin", "ETH": "Ethereum", "BNB": "BNB",
    "SOL": "Solana", "XRP": "XRP", "ADA": "Cardano",
    "AVAX": "Avalanche", "DOGE": "Dogecoin", "DOT": "Polkadot",
    "MATIC": "Polygon", "LINK": "Chainlink", "UNI": "Uniswap",
}

LABEL_COLORS = {
    "bullish":    "#10B981",
    "bearish":    "#F87171",
    "regulatory": "#8B5CF6",
    "technical":  "#3B82F6",
    "macro":      "#FBBF24",
}


def load_classified_news(path="data/classified_news.csv"):
    df = pd.read_csv(path)
    return df


def get_label_distribution(df):
    """Overall label distribution."""
    counts = df["primary_label"].value_counts().reset_index()
    counts.columns = ["label", "count"]
    counts["pct"] = (counts["count"] / len(df) * 100).round(1)
    return counts


def get_ticker_distribution(df):
    """Which crypto tickers appear most in news."""
    all_tickers = []
    for val in df["tickers"]:
        try:
            if isinstance(val, str):
                tickers = ast.literal_eval(val)
            else:
                tickers = val
            all_tickers.extend([t for t in tickers if t != "OTHER"])
        except:
            pass
    ticker_counts = Counter(all_tickers)
    ticker_df = pd.DataFrame(
        ticker_counts.most_common(12),
        columns=["ticker", "count"]
    )
    return ticker_df


def get_ticker_sentiment(df):
    """Sentiment breakdown per ticker."""
    rows = []
    for _, row in df.iterrows():
        try:
            tickers = ast.literal_eval(row["tickers"]) if isinstance(row["tickers"], str) else row["tickers"]
        except:
            tickers = ["OTHER"]
        for ticker in tickers:
            if ticker != "OTHER":
                rows.append({
                    "ticker": ticker,
                    "label": row["primary_label"],
                    "score_bullish": row.get("score_bullish", 0),
                    "score_bearish": row.get("score_bearish", 0),
                })

    if not rows:
        return pd.DataFrame()

    sent_df = pd.DataFrame(rows)
    pivot = sent_df.groupby(["ticker", "label"]).size().unstack(fill_value=0).reset_index()
    return pivot


def get_source_distribution(df):
    """News source distribution."""
    source_counts = df["source"].value_counts().head(10).reset_index()
    source_counts.columns = ["source", "count"]
    return source_counts


def get_market_sentiment_score(df):
    """
    Composite market sentiment score 0-100.
    Based on bullish vs bearish ratio.
    """
    bullish_count = (df["primary_label"] == "bullish").sum()
    bearish_count = (df["primary_label"] == "bearish").sum()
    total = len(df)

    if total == 0:
        return 50.0

    bull_pct = bullish_count / total
    bear_pct = bearish_count / total
    score = 50 + (bull_pct - bear_pct) * 50
    return round(min(max(score, 0), 100), 1)


def get_score_heatmap(df):
    """Score matrix for heatmap — tickers vs label scores."""
    rows = []
    for _, row in df.iterrows():
        try:
            tickers = ast.literal_eval(row["tickers"]) if isinstance(row["tickers"], str) else row["tickers"]
        except:
            tickers = ["OTHER"]
        for ticker in tickers:
            if ticker != "OTHER":
                rows.append({
                    "ticker": ticker,
                    "bullish": row.get("score_bullish", 0),
                    "bearish": row.get("score_bearish", 0),
                    "regulatory": row.get("score_regulatory", 0),
                    "technical": row.get("score_technical", 0),
                    "macro": row.get("score_macro", 0),
                })

    if not rows:
        return pd.DataFrame()

    heat_df = pd.DataFrame(rows)
    heat_df = heat_df.groupby("ticker").mean().round(4).reset_index()
    return heat_df


def get_multi_label_counts(df):
    """Count articles with multiple labels."""
    df = df.copy()
    df["label_count"] = df["active_labels"].apply(
        lambda x: len(str(x).split(",")) if pd.notna(x) else 1
    )
    return df["label_count"].value_counts().reset_index().rename(
        columns={"index": "num_labels", "label_count": "count"}
    )


if __name__ == "__main__":
    df = load_classified_news()
    print(f"Loaded {len(df)} classified articles\n")

    print("--- Label Distribution ---")
    print(get_label_distribution(df).to_string(index=False))

    print("\n--- Ticker Mentions ---")
    print(get_ticker_distribution(df).to_string(index=False))

    print("\n--- Market Sentiment Score ---")
    score = get_market_sentiment_score(df)
    print(f"Score: {score}/100")

    print("\n--- Source Distribution ---")
    print(get_source_distribution(df).to_string(index=False))

    heat_df = get_score_heatmap(df)
    if not heat_df.empty:
        heat_df.to_csv("data/sentiment_heatmap.csv", index=False)
        print("\nSaved data/sentiment_heatmap.csv")