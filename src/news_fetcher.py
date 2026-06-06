"""
Crypto & financial news fetcher.
Uses free public APIs — no API key required.
Sources: CoinGecko news, Crypto Panic public feed, RSS feeds.
"""

import requests
import pandas as pd
from datetime import datetime, timedelta
import time
import os
import re


CRYPTO_TICKERS = {
    "BTC": "Bitcoin", "ETH": "Ethereum", "BNB": "BNB",
    "SOL": "Solana", "XRP": "XRP", "ADA": "Cardano",
    "AVAX": "Avalanche", "DOGE": "Dogecoin", "DOT": "Polkadot",
    "MATIC": "Polygon", "LINK": "Chainlink", "UNI": "Uniswap",
}

CRYPTO_EXCHANGES = [
    "Binance", "Coinbase", "Kraken", "OKX", "Bybit",
    "Huobi", "FTX", "Gemini", "Bitstamp", "KuCoin",
]

MACRO_KEYWORDS = [
    "Federal Reserve", "Fed", "interest rate", "inflation", "CPI",
    "recession", "GDP", "SEC", "CFTC", "regulation", "ETF",
    "institutional", "BlackRock", "Fidelity", "JPMorgan",
]


def fetch_coingecko_news(limit=50):
    """Fetch crypto news from CoinGecko public API."""
    url = "https://api.coingecko.com/api/v3/news"
    headers = {"accept": "application/json"}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            articles = data.get("data", [])[:limit]
            rows = []
            for a in articles:
                rows.append({
                    "title": a.get("title", ""),
                    "description": a.get("description", ""),
                    "url": a.get("url", ""),
                    "source": a.get("news_site", ""),
                    "published_at": a.get("updated_at", ""),
                    "api_source": "coingecko",
                })
            print(f"CoinGecko: fetched {len(rows)} articles")
            return rows
        else:
            print(f"CoinGecko error: {response.status_code}")
            return []
    except Exception as e:
        print(f"CoinGecko fetch failed: {e}")
        return []


def fetch_cryptopanic_news(limit=50):
    """Fetch from CryptoPanic public RSS/API."""
    url = "https://cryptopanic.com/api/free/v1/posts/?auth_token=&public=true"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            results = data.get("results", [])[:limit]
            rows = []
            for a in results:
                rows.append({
                    "title": a.get("title", ""),
                    "description": a.get("title", ""),
                    "url": a.get("url", ""),
                    "source": a.get("source", {}).get("title", ""),
                    "published_at": a.get("published_at", ""),
                    "api_source": "cryptopanic",
                })
            print(f"CryptoPanic: fetched {len(rows)} articles")
            return rows
        else:
            print(f"CryptoPanic error: {response.status_code}")
            return []
    except Exception as e:
        print(f"CryptoPanic fetch failed: {e}")
        return []


def generate_sample_news():
    """Generate realistic sample crypto news for demo/offline use."""
    sample_articles = [
        {"title": "Bitcoin surges past $70,000 as institutional demand hits record highs", "source": "CoinDesk"},
        {"title": "SEC approves spot Ethereum ETF applications from BlackRock and Fidelity", "source": "Reuters"},
        {"title": "Federal Reserve holds interest rates steady, crypto markets rally on dovish signal", "source": "Bloomberg"},
        {"title": "Binance faces new regulatory scrutiny from CFTC over derivatives trading", "source": "WSJ"},
        {"title": "Solana network processes 65,000 transactions per second in stress test", "source": "The Block"},
        {"title": "Bitcoin mining difficulty reaches all-time high ahead of halving event", "source": "CoinTelegraph"},
        {"title": "Ethereum gas fees drop 80 percent following Dencun upgrade", "source": "Decrypt"},
        {"title": "JPMorgan upgrades Coinbase stock to buy citing crypto market momentum", "source": "CNBC"},
        {"title": "XRP wins partial victory against SEC in landmark court ruling", "source": "Reuters"},
        {"title": "Crypto markets crash 15 percent after surprise CPI inflation data", "source": "Bloomberg"},
        {"title": "Avalanche launches $100 million ecosystem fund for DeFi developers", "source": "CoinDesk"},
        {"title": "Dogecoin surges 40 percent after Elon Musk tweets support", "source": "CoinTelegraph"},
        {"title": "Cardano smart contract activity hits 6-month high on network growth", "source": "Decrypt"},
        {"title": "Chainlink CCIP goes live on Ethereum mainnet for cross-chain transactions", "source": "The Block"},
        {"title": "BNB Chain introduces new gas fee reduction mechanism for validators", "source": "CoinDesk"},
        {"title": "Uniswap v4 launches with hooks feature enabling custom liquidity pools", "source": "Decrypt"},
        {"title": "Bitcoin ETF inflows exceed $500 million in single day trading session", "source": "Bloomberg"},
        {"title": "Polkadot parachain auctions resume after governance vote passes", "source": "CoinTelegraph"},
        {"title": "KuCoin reaches settlement with US prosecutors over AML violations", "source": "WSJ"},
        {"title": "Crypto regulatory framework passes EU Parliament in landmark vote", "source": "Reuters"},
        {"title": "Polygon zkEVM processes one million transactions in first month", "source": "The Block"},
        {"title": "Bitcoin dominance falls to 48 percent as altcoin season begins", "source": "CoinDesk"},
        {"title": "Ethereum staking yields rise to 5.2 percent as validator queue grows", "source": "Decrypt"},
        {"title": "Kraken expands to Australian market with new exchange licence", "source": "CoinTelegraph"},
        {"title": "BlackRock Bitcoin ETF becomes largest crypto fund with $20 billion AUM", "source": "Bloomberg"},
    ]
    rows = []
    for i, a in enumerate(sample_articles):
        rows.append({
            "title": a["title"],
            "description": a["title"],
            "url": f"https://example.com/article-{i}",
            "source": a["source"],
            "published_at": datetime.now().isoformat(),
            "api_source": "sample",
        })
    return rows


def fetch_all_news(use_sample_fallback=True):
    """Fetch from all sources, fall back to sample if APIs fail."""
    all_articles = []
    all_articles.extend(fetch_coingecko_news(30))
    time.sleep(1)
    all_articles.extend(fetch_cryptopanic_news(30))

    if len(all_articles) < 5 and use_sample_fallback:
        print("APIs returned insufficient data — using sample news dataset")
        all_articles = generate_sample_news()

    df = pd.DataFrame(all_articles)
    df = df.drop_duplicates(subset=["title"])
    df = df[df["title"].str.len() > 10]
    df = df.reset_index(drop=True)
    print(f"Total unique articles: {len(df)}")
    return df


def tag_tickers(title):
    """Tag which crypto tickers are mentioned."""
    found = []
    title_upper = title.upper()
    for ticker, name in CRYPTO_TICKERS.items():
        if ticker in title_upper or name.lower() in title.lower():
            found.append(ticker)
    return found if found else ["OTHER"]


def tag_exchanges(title):
    """Tag which exchanges are mentioned."""
    found = [ex for ex in CRYPTO_EXCHANGES if ex.lower() in title.lower()]
    return found if found else []


def tag_macro(title):
    """Tag macro/regulatory keywords."""
    found = [kw for kw in MACRO_KEYWORDS if kw.lower() in title.lower()]
    return found if found else []


if __name__ == "__main__":
    os.makedirs("data", exist_ok=True)
    df = fetch_all_news()
    df["tickers"] = df["title"].apply(tag_tickers)
    df["exchanges"] = df["title"].apply(tag_exchanges)
    df["macro_tags"] = df["title"].apply(tag_macro)
    df.to_csv("data/raw_news.csv", index=False)
    print(df[["title", "source", "tickers"]].head(10).to_string(index=False))
    print(f"\nSaved {len(df)} articles to data/raw_news.csv")