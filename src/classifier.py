"""
Multi-label crypto news classifier.
Classifies headlines into: bullish, bearish, regulatory, technical, macro
Uses zero-shot classification with HuggingFace pipeline.
"""

from transformers import pipeline
import pandas as pd
import numpy as np
import os

LABELS = ["bullish", "bearish", "regulatory", "technical", "macro"]

LABEL_COLORS = {
    "bullish":    "#10B981",
    "bearish":    "#F87171",
    "regulatory": "#8B5CF6",
    "technical":  "#3B82F6",
    "macro":      "#FBBF24",
}

LABEL_EMOJIS = {
    "bullish":    "🟢",
    "bearish":    "🔴",
    "regulatory": "⚖️",
    "technical":  "⚙️",
    "macro":      "🌍",
}

LABEL_DESCRIPTIONS = {
    "bullish":    "positive price movement, gains, growth, surge, rally, upward",
    "bearish":    "negative price movement, crash, decline, drop, loss, downward",
    "regulatory": "SEC, CFTC, law, regulation, compliance, government, ban, approval",
    "technical":  "protocol upgrade, network, blockchain, smart contract, DeFi, staking",
    "macro":      "Federal Reserve, interest rates, inflation, GDP, institutional, ETF",
}


def load_classifier():
    """Load zero-shot classification pipeline."""
    print("Loading zero-shot classifier...")
    classifier = pipeline(
        "zero-shot-classification",
        model="facebook/bart-large-mnli",
        device=-1,
    )
    return classifier


def classify_headline(headline, classifier, threshold=0.15):
    """Classify a single headline into multiple labels."""
    candidate_labels = list(LABEL_DESCRIPTIONS.values())
    label_keys = list(LABEL_DESCRIPTIONS.keys())

    result = classifier(
        headline,
        candidate_labels=candidate_labels,
        multi_label=True,
    )

    label_scores = {}
    for label_desc, score in zip(result["labels"], result["scores"]):
        idx = candidate_labels.index(label_desc)
        label_key = label_keys[idx]
        label_scores[label_key] = round(score, 4)

    active_labels = [l for l, s in label_scores.items() if s >= threshold]
    if not active_labels:
        active_labels = [max(label_scores, key=label_scores.get)]

    primary_label = max(label_scores, key=label_scores.get)

    return {
        "primary_label": primary_label,
        "active_labels": active_labels,
        "scores": label_scores,
        "emoji": LABEL_EMOJIS[primary_label],
        "color": LABEL_COLORS[primary_label],
    }


def classify_dataframe(df, classifier, text_col="title"):
    """Classify all headlines in a dataframe."""
    print(f"Classifying {len(df)} headlines...")
    results = []
    for i, row in df.iterrows():
        if i % 5 == 0:
            print(f"  {i+1}/{len(df)}...")
        result = classify_headline(row[text_col], classifier)
        results.append(result)

    df = df.copy()
    df["primary_label"]  = [r["primary_label"] for r in results]
    df["active_labels"]  = [",".join(r["active_labels"]) for r in results]
    df["score_bullish"]  = [r["scores"]["bullish"] for r in results]
    df["score_bearish"]  = [r["scores"]["bearish"] for r in results]
    df["score_regulatory"] = [r["scores"]["regulatory"] for r in results]
    df["score_technical"]  = [r["scores"]["technical"] for r in results]
    df["score_macro"]    = [r["scores"]["macro"] for r in results]
    df["emoji"]          = [r["emoji"] for r in results]
    return df


def rule_based_classify(title):
    """
    Fast rule-based classifier — no model needed.
    Used as fallback and for Streamlit Cloud deployment.
    """
    title_lower = title.lower()
    scores = {l: 0.0 for l in LABELS}

    bullish_words = ["surge", "rally", "gains", "soar", "record", "high", "bullish",
                     "approval", "buy", "upgrade", "launch", "growth", "wins", "rises",
                     "expands", "inflows", "milestone", "breakthrough", "exceeds"]
    bearish_words = ["crash", "drop", "fall", "decline", "loss", "bearish", "plunge",
                     "fears", "risk", "warning", "sell", "down", "collapse", "crisis",
                     "hack", "exploit", "scam", "fraud", "liquidation", "tumbles"]
    regulatory_words = ["sec", "cftc", "regulation", "regulatory", "law", "legal",
                        "court", "ruling", "ban", "compliance", "settlement", "licence",
                        "framework", "policy", "government", "congress", "senate"]
    technical_words = ["protocol", "upgrade", "network", "blockchain", "smart contract",
                       "defi", "staking", "validator", "mainnet", "testnet", "layer",
                       "bridge", "liquidity", "gas", "transactions", "nodes", "fork"]
    macro_words = ["federal reserve", "fed", "interest rate", "inflation", "cpi", "gdp",
                   "recession", "institutional", "blackrock", "fidelity", "jpmorgan",
                   "etf", "macro", "economy", "monetary", "treasury"]

    for w in bullish_words:
        if w in title_lower: scores["bullish"] += 0.3
    for w in bearish_words:
        if w in title_lower: scores["bearish"] += 0.3
    for w in regulatory_words:
        if w in title_lower: scores["regulatory"] += 0.3
    for w in technical_words:
        if w in title_lower: scores["technical"] += 0.3
    for w in macro_words:
        if w in title_lower: scores["macro"] += 0.3

    # Normalize
    total = sum(scores.values()) or 1.0
    scores = {k: round(v / total, 4) for k, v in scores.items()}

    # Ensure minimum scores
    for k in scores:
        scores[k] = max(scores[k], 0.05)

    active_labels = [l for l, s in scores.items() if s >= 0.15]
    primary_label = max(scores, key=scores.get)
    if not active_labels:
        active_labels = [primary_label]

    return {
        "primary_label":   primary_label,
        "active_labels":   active_labels,
        "scores":          scores,
        "emoji":           LABEL_EMOJIS[primary_label],
        "color":           LABEL_COLORS[primary_label],
    }


def classify_dataframe_fast(df, text_col="title"):
    """Rule-based classification — fast, no model download."""
    print(f"Classifying {len(df)} headlines (rule-based)...")
    results = [rule_based_classify(row[text_col]) for _, row in df.iterrows()]

    df = df.copy()
    df["primary_label"]    = [r["primary_label"] for r in results]
    df["active_labels"]    = [",".join(r["active_labels"]) for r in results]
    df["score_bullish"]    = [r["scores"]["bullish"] for r in results]
    df["score_bearish"]    = [r["scores"]["bearish"] for r in results]
    df["score_regulatory"] = [r["scores"]["regulatory"] for r in results]
    df["score_technical"]  = [r["scores"]["technical"] for r in results]
    df["score_macro"]      = [r["scores"]["macro"] for r in results]
    df["emoji"]            = [r["emoji"] for r in results]
    return df


if __name__ == "__main__":
    csv_path = "data/raw_news.csv"
    if not os.path.exists(csv_path):
        print("Run news_fetcher.py first")
    else:
        df = pd.read_csv(csv_path)
        df = classify_dataframe_fast(df)

        print("\n--- Classification Results ---")
        for _, row in df.head(10).iterrows():
            print(f"{row['emoji']} {row['primary_label'].upper():12} | {row['title'][:70]}")

        os.makedirs("data", exist_ok=True)
        df.to_csv("data/classified_news.csv", index=False)
        print(f"\nLabel distribution:")
        print(df["primary_label"].value_counts())
        print("\nSaved data/classified_news.csv")