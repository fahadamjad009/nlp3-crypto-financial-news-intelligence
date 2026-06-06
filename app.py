"""
NLP3 — Crypto & Financial News Intelligence
Interactive dashboard: multi-label classification, trend detection,
sentiment scoring, ticker analysis, source breakdown.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import sys, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))
from news_fetcher import fetch_all_news, tag_tickers, tag_exchanges, tag_macro, generate_sample_news
from classifier import classify_dataframe_fast, LABEL_COLORS, LABEL_EMOJIS, LABELS
from trend_detector import (
    get_label_distribution, get_ticker_distribution, get_ticker_sentiment,
    get_source_distribution, get_market_sentiment_score, get_score_heatmap,
    get_multi_label_counts,
)

st.set_page_config(
    page_title="Crypto News Intelligence",
    page_icon="₿",
    layout="wide",
)

st.markdown("""
<style>
    .main { background-color: #0A0F1E; }
    .block-container { padding-top: 1.5rem; padding-left: 2rem; padding-right: 2rem; }
    .stButton > button {
        background: linear-gradient(90deg, #92400E, #F7931A);
        color: white; border: none; border-radius: 10px;
        padding: 0.5rem 2rem; font-size: 1rem; font-weight: 600;
    }
    .stButton > button:hover { background: linear-gradient(90deg, #B45309, #FBBF24); }
    .news-card {
        background: linear-gradient(135deg, #0F172A, #1C1F2E);
        border-left: 4px solid #F7931A;
        border-radius: 0 12px 12px 0;
        padding: 0.8rem 1.2rem;
        margin: 0.4rem 0;
    }
    .footer { color: #475569; font-size: 0.78rem; text-align: center; margin-top: 2rem; }
    h1 { background: linear-gradient(90deg, #F7931A, #FBBF24);
         -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
    [data-testid="stMetricValue"] { color: #F1F5F9 !important; }
</style>
""", unsafe_allow_html=True)

PLOT_BG  = "#0A0F1E"
PAPER_BG = "#111827"
GRID_COL = "#1E3A5F"
TEXT_COL = "#94A3B8"
ORANGE   = "#F7931A"

def dark_layout(fig, title="", height=350):
    fig.update_layout(
        title=dict(text=title, font=dict(color="#F1F5F9", size=14)),
        plot_bgcolor=PLOT_BG, paper_bgcolor=PAPER_BG,
        font=dict(color=TEXT_COL), height=height,
        margin=dict(l=20, r=20, t=40, b=20),
    )
    return fig

# ── Session state ─────────────────────────────────────────────────────────────
if "df" not in st.session_state:
    st.session_state.df = None
if "loaded" not in st.session_state:
    st.session_state.loaded = False

# ── Header ────────────────────────────────────────────────────────────────────
st.title("₿ Crypto & Financial News Intelligence")
st.markdown(
    "Real-time crypto news pipeline — **multi-label classification**, "
    "**ticker trend detection**, **market sentiment scoring**, "
    "**source analysis**, and **interactive visualisations**. "
    "Powered by rule-based NLP · spaCy · Plotly · Streamlit"
)
st.markdown("---")

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("⚙️ Controls")
    if st.button("🔄 Fetch Latest News", type="primary"):
        with st.spinner("Fetching and classifying news..."):
            df = fetch_all_news(use_sample_fallback=True)
            df["tickers"]     = df["title"].apply(tag_tickers)
            df["exchanges"]   = df["title"].apply(tag_exchanges)
            df["macro_tags"]  = df["title"].apply(tag_macro)
            df = classify_dataframe_fast(df)
            st.session_state.df = df
            st.session_state.loaded = True
            df.to_csv("data/classified_news.csv", index=False)
        st.success(f"Loaded {len(df)} articles.")

    if st.button("📂 Load Sample Dataset"):
        import ast
        if os.path.exists("data/classified_news.csv"):
            df = pd.read_csv("data/classified_news.csv")
            st.session_state.df = df
            st.session_state.loaded = True
            st.success(f"Loaded {len(df)} articles from cache.")
        else:
            df_raw = pd.DataFrame(generate_sample_news())
            df_raw["tickers"]    = df_raw["title"].apply(tag_tickers)
            df_raw["exchanges"]  = df_raw["title"].apply(tag_exchanges)
            df_raw["macro_tags"] = df_raw["title"].apply(tag_macro)
            df = classify_dataframe_fast(df_raw)
            st.session_state.df = df
            st.session_state.loaded = True
            st.success(f"Generated {len(df)} sample articles.")

    st.markdown("---")
    st.markdown("**Filters**")
    label_filter = st.multiselect(
        "Filter by label:",
        options=LABELS,
        default=LABELS,
    )
    st.markdown("---")
    st.caption("Data: CoinGecko · CryptoPanic · Sample fallback")

# ══════════════════════════════════════════════════════════════════════════════
if st.session_state.loaded and st.session_state.df is not None:
    df_full = st.session_state.df
    df = df_full[df_full["primary_label"].isin(label_filter)] if label_filter else df_full

    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Market Overview",
        "📰 News Feed",
        "₿ Ticker Analysis",
        "🔥 Trend Heatmap",
        "📡 Source Intelligence",
    ])

    # ══════════════════════════════════════════════════════════════════════════
    # TAB 1 — MARKET OVERVIEW
    # ══════════════════════════════════════════════════════════════════════════
    with tab1:
        st.subheader("Market Overview")

        score = get_market_sentiment_score(df)
        label_dist = get_label_distribution(df)
        bull = (df["primary_label"] == "bullish").sum()
        bear = (df["primary_label"] == "bearish").sum()
        reg  = (df["primary_label"] == "regulatory").sum()

        c1, c2, c3, c4, c5 = st.columns(5)
        c1.metric("Total Articles", len(df))
        c2.metric("Market Score", f"{score}/100")
        c3.metric("🟢 Bullish", bull)
        c4.metric("🔴 Bearish", bear)
        c5.metric("⚖️ Regulatory", reg)

        st.markdown("---")
        col_gauge, col_pie = st.columns(2)

        with col_gauge:
            fig_gauge = go.Figure(go.Indicator(
                mode="gauge+number+delta",
                value=score,
                delta={"reference": 50, "valueformat": ".1f"},
                title={"text": "Market Sentiment Score", "font": {"color": "#F1F5F9", "size": 16}},
                number={"font": {"color": ORANGE, "size": 48}, "suffix": "/100"},
                gauge={
                    "axis": {"range": [0, 100], "tickcolor": TEXT_COL},
                    "bar":  {"color": ORANGE},
                    "bgcolor": PAPER_BG,
                    "steps": [
                        {"range": [0,  35], "color": "#7F1D1D"},
                        {"range": [35, 65], "color": "#78350F"},
                        {"range": [65, 100],"color": "#064E3B"},
                    ],
                    "threshold": {
                        "line": {"color": "#FBBF24", "width": 4},
                        "thickness": 0.75,
                        "value": score,
                    },
                },
            ))
            fig_gauge.update_layout(
                paper_bgcolor=PAPER_BG, font={"color": TEXT_COL},
                height=320, margin=dict(l=30, r=30, t=60, b=20),
            )
            st.plotly_chart(fig_gauge, use_container_width=True)

        with col_pie:
            fig_pie = go.Figure(go.Pie(
                labels=[l.upper() for l in label_dist["label"]],
                values=label_dist["count"],
                hole=0.55,
                marker_colors=[LABEL_COLORS.get(l, ORANGE) for l in label_dist["label"]],
                text=[f"{p}%" for p in label_dist["pct"]],
            ))
            fig_pie = dark_layout(fig_pie, "Label Distribution", 320)
            st.plotly_chart(fig_pie, use_container_width=True)

        # Label bar chart
        fig_bar = go.Figure(go.Bar(
            x=[l.upper() for l in label_dist["label"]],
            y=label_dist["count"],
            marker_color=[LABEL_COLORS.get(l, ORANGE) for l in label_dist["label"]],
            text=label_dist["count"],
            textposition="outside",
        ))
        fig_bar = dark_layout(fig_bar, "Articles per Label", 300)
        fig_bar.update_xaxes(showgrid=False)
        fig_bar.update_yaxes(gridcolor=GRID_COL)
        st.plotly_chart(fig_bar, use_container_width=True)

        # Score distribution per label
        st.markdown("---")
        st.subheader("📈 Score Distribution per Label")
        score_cols = ["score_bullish","score_bearish","score_regulatory","score_technical","score_macro"]
        available = [c for c in score_cols if c in df.columns]
        if available:
            fig_box = go.Figure()
            for col in available:
                label_name = col.replace("score_","")
                fig_box.add_trace(go.Box(
                    y=df[col],
                    name=label_name.upper(),
                    marker_color=LABEL_COLORS.get(label_name, ORANGE),
                    boxmean=True,
                ))
            fig_box = dark_layout(fig_box, "Score Distribution (Box Plot)", 380)
            fig_box.update_yaxes(gridcolor=GRID_COL)
            fig_box.update_layout(showlegend=False)
            st.plotly_chart(fig_box, use_container_width=True)

    # ══════════════════════════════════════════════════════════════════════════
    # TAB 2 — NEWS FEED
    # ══════════════════════════════════════════════════════════════════════════
    with tab2:
        st.subheader("📰 Live News Feed")

        search = st.text_input("🔍 Search headlines:", "")
        sort_by = st.selectbox("Sort by:", ["Default", "Most Bullish", "Most Bearish", "Regulatory First"])

        feed_df = df.copy()
        if search:
            feed_df = feed_df[feed_df["title"].str.contains(search, case=False, na=False)]

        if sort_by == "Most Bullish":
            feed_df = feed_df.sort_values("score_bullish", ascending=False)
        elif sort_by == "Most Bearish":
            feed_df = feed_df.sort_values("score_bearish", ascending=False)
        elif sort_by == "Regulatory First":
            feed_df = feed_df.sort_values("score_regulatory", ascending=False)

        st.caption(f"Showing {len(feed_df)} articles")

        for _, row in feed_df.iterrows():
            label = row.get("primary_label", "unknown")
            emoji = LABEL_EMOJIS.get(label, "📰")
            color = LABEL_COLORS.get(label, ORANGE)
            tickers = row.get("tickers", "[]")
            try:
                import ast
                ticker_list = ast.literal_eval(str(tickers))
                ticker_str = " · ".join([f"`{t}`" for t in ticker_list if t != "OTHER"])
            except:
                ticker_str = ""

            st.markdown(
                f"<div class='news-card' style='border-left-color:{color}'>"
                f"<span style='color:{color}; font-weight:700; font-size:0.85rem'>"
                f"{emoji} {label.upper()}</span>"
                f"<span style='color:#475569; font-size:0.78rem; margin-left:1rem'>"
                f"{row.get('source','')}</span><br>"
                f"<span style='color:#F1F5F9'>{row['title']}</span><br>"
                f"<span style='color:#94A3B8; font-size:0.78rem'>{ticker_str}</span>"
                f"</div>",
                unsafe_allow_html=True,
            )

        st.markdown("---")
        st.markdown("**Full Data Table**")
        display_cols = ["title","primary_label","active_labels","source","tickers"]
        available_cols = [c for c in display_cols if c in df.columns]
        st.dataframe(
            feed_df[available_cols].rename(columns={
                "title":"Headline","primary_label":"Label",
                "active_labels":"All Labels","source":"Source","tickers":"Tickers"
            }),
            use_container_width=True, hide_index=True,
        )

    # ══════════════════════════════════════════════════════════════════════════
    # TAB 3 — TICKER ANALYSIS
    # ══════════════════════════════════════════════════════════════════════════
    with tab3:
        st.subheader("₿ Crypto Ticker Analysis")

        ticker_dist = get_ticker_distribution(df)

        if ticker_dist.empty:
            st.info("No specific tickers found in current articles.")
        else:
            col_a, col_b = st.columns(2)

            with col_a:
                fig_tick = go.Figure(go.Bar(
                    x=ticker_dist["ticker"],
                    y=ticker_dist["count"],
                    marker_color=ORANGE,
                    text=ticker_dist["count"],
                    textposition="outside",
                ))
                fig_tick = dark_layout(fig_tick, "Ticker Mention Frequency", 320)
                fig_tick.update_xaxes(showgrid=False)
                fig_tick.update_yaxes(gridcolor=GRID_COL)
                st.plotly_chart(fig_tick, use_container_width=True)

            with col_b:
                fig_tick_pie = go.Figure(go.Pie(
                    labels=ticker_dist["ticker"],
                    values=ticker_dist["count"],
                    hole=0.45,
                    marker_colors=px.colors.qualitative.Bold,
                ))
                fig_tick_pie = dark_layout(fig_tick_pie, "Ticker Share of Coverage", 320)
                st.plotly_chart(fig_tick_pie, use_container_width=True)

            # Ticker sentiment breakdown
            st.markdown("---")
            st.subheader("Ticker Sentiment Breakdown")
            ticker_sent = get_ticker_sentiment(df)
            if not ticker_sent.empty:
                label_cols = [c for c in ["bullish","bearish","regulatory","technical","macro"]
                              if c in ticker_sent.columns]
                fig_stacked = go.Figure()
                for lc in label_cols:
                    fig_stacked.add_trace(go.Bar(
                        name=lc.upper(),
                        x=ticker_sent["ticker"],
                        y=ticker_sent[lc],
                        marker_color=LABEL_COLORS.get(lc, ORANGE),
                    ))
                fig_stacked = dark_layout(fig_stacked, "Sentiment per Ticker (Stacked)", 380)
                fig_stacked.update_layout(
                    barmode="stack",
                    legend=dict(bgcolor="rgba(0,0,0,0)"),
                )
                fig_stacked.update_xaxes(showgrid=False)
                fig_stacked.update_yaxes(gridcolor=GRID_COL)
                st.plotly_chart(fig_stacked, use_container_width=True)

            # Ticker sentiment scatter
            heat_df = get_score_heatmap(df)
            if not heat_df.empty and "bullish" in heat_df.columns and "bearish" in heat_df.columns:
                fig_scat = go.Figure(go.Scatter(
                    x=heat_df["bullish"],
                    y=heat_df["bearish"],
                    mode="markers+text",
                    text=heat_df["ticker"],
                    textposition="top center",
                    marker=dict(
                        size=18,
                        color=heat_df["bullish"],
                        colorscale="RdYlGn",
                        showscale=True,
                        colorbar=dict(title="Bullish Score"),
                        line=dict(color="#0A0F1E", width=2),
                    ),
                    hovertemplate="<b>%{text}</b><br>Bullish: %{x:.2f}<br>Bearish: %{y:.2f}",
                ))
                fig_scat = dark_layout(fig_scat, "Bullish vs Bearish Score per Ticker", 380)
                fig_scat.update_xaxes(title="Bullish Score", gridcolor=GRID_COL)
                fig_scat.update_yaxes(title="Bearish Score", gridcolor=GRID_COL)
                st.plotly_chart(fig_scat, use_container_width=True)

    # ══════════════════════════════════════════════════════════════════════════
    # TAB 4 — TREND HEATMAP
    # ══════════════════════════════════════════════════════════════════════════
    with tab4:
        st.subheader("🔥 Sentiment Trend Heatmap")
        st.caption("Average label scores per crypto ticker — brighter = stronger signal")

        heat_df = get_score_heatmap(df)

        if heat_df.empty:
            st.info("No ticker data available for heatmap.")
        else:
            score_cols = ["bullish","bearish","regulatory","technical","macro"]
            available = [c for c in score_cols if c in heat_df.columns]
            z_data = heat_df[available].values
            x_labels = [c.upper() for c in available]
            y_labels = heat_df["ticker"].tolist()

            fig_heat = go.Figure(go.Heatmap(
                z=z_data,
                x=x_labels,
                y=y_labels,
                colorscale="YlOrRd",
                hovertemplate="Ticker: %{y}<br>Label: %{x}<br>Score: %{z:.3f}<extra></extra>",
                colorbar=dict(title="Avg Score"),
            ))
            fig_heat = dark_layout(fig_heat, "Ticker x Label Sentiment Heatmap", 500)
            fig_heat.update_xaxes(showgrid=False)
            fig_heat.update_yaxes(showgrid=False)
            st.plotly_chart(fig_heat, use_container_width=True)

            # Radar chart per ticker
            st.markdown("---")
            st.subheader("📡 Ticker Sentiment Radar")
            selected_ticker = st.selectbox("Select ticker:", heat_df["ticker"].tolist())
            ticker_row = heat_df[heat_df["ticker"] == selected_ticker].iloc[0]
            radar_values = [ticker_row.get(c, 0) for c in available]
            radar_values.append(radar_values[0])
            radar_labels = x_labels + [x_labels[0]]

            fig_radar = go.Figure(go.Scatterpolar(
                r=radar_values,
                theta=radar_labels,
                fill="toself",
                fillcolor="rgba(247,147,26,0.2)",
                line=dict(color=ORANGE, width=2),
                marker=dict(color=ORANGE, size=8),
            ))
            fig_radar.update_layout(
                polar=dict(
                    radialaxis=dict(visible=True, range=[0, 0.5], gridcolor=GRID_COL),
                    angularaxis=dict(gridcolor=GRID_COL),
                    bgcolor=PLOT_BG,
                ),
                paper_bgcolor=PAPER_BG,
                font=dict(color=TEXT_COL),
                height=400,
                title=dict(text=f"{selected_ticker} Sentiment Radar", font=dict(color="#F1F5F9")),
                margin=dict(l=60, r=60, t=60, b=40),
            )
            st.plotly_chart(fig_radar, use_container_width=True)

            # Multi-label distribution
            st.markdown("---")
            st.subheader("🏷️ Multi-label Distribution")
            multi_df = get_multi_label_counts(df)
            fig_multi = go.Figure(go.Bar(
                x=["1 label","2 labels","3+ labels"][:len(multi_df)],
                y=multi_df.iloc[:, 1].tolist(),
                marker_color=ORANGE,
                text=multi_df.iloc[:, 1].tolist(),
                textposition="outside",
            ))
            fig_multi = dark_layout(fig_multi, "Articles by Number of Labels", 280)
            fig_multi.update_xaxes(showgrid=False)
            fig_multi.update_yaxes(gridcolor=GRID_COL)
            st.plotly_chart(fig_multi, use_container_width=True)

    # ══════════════════════════════════════════════════════════════════════════
    # TAB 5 — SOURCE INTELLIGENCE
    # ══════════════════════════════════════════════════════════════════════════
    with tab5:
        st.subheader("📡 News Source Intelligence")

        source_dist = get_source_distribution(df)

        col_a, col_b = st.columns(2)
        with col_a:
            fig_src = go.Figure(go.Bar(
                x=source_dist["count"],
                y=source_dist["source"],
                orientation="h",
                marker_color=ORANGE,
                text=source_dist["count"],
                textposition="outside",
            ))
            fig_src = dark_layout(fig_src, "Articles per Source", 350)
            fig_src.update_xaxes(gridcolor=GRID_COL)
            fig_src.update_yaxes(showgrid=False, autorange="reversed")
            st.plotly_chart(fig_src, use_container_width=True)

        with col_b:
            fig_src_pie = go.Figure(go.Pie(
                labels=source_dist["source"],
                values=source_dist["count"],
                hole=0.4,
                marker_colors=px.colors.qualitative.Bold,
            ))
            fig_src_pie = dark_layout(fig_src_pie, "Source Share", 350)
            st.plotly_chart(fig_src_pie, use_container_width=True)

        # Source sentiment breakdown
        st.markdown("---")
        st.subheader("Source Sentiment Profile")
        src_sent = df.groupby(["source","primary_label"]).size().unstack(fill_value=0).reset_index()
        label_cols = [c for c in LABELS if c in src_sent.columns]
        if label_cols:
            fig_src_stack = go.Figure()
            for lc in label_cols:
                fig_src_stack.add_trace(go.Bar(
                    name=lc.upper(),
                    x=src_sent["source"],
                    y=src_sent[lc],
                    marker_color=LABEL_COLORS.get(lc, ORANGE),
                ))
            fig_src_stack = dark_layout(fig_src_stack, "Sentiment Breakdown per Source", 380)
            fig_src_stack.update_layout(
                barmode="stack",
                legend=dict(bgcolor="rgba(0,0,0,0)"),
            )
            fig_src_stack.update_xaxes(tickangle=-30, showgrid=False)
            fig_src_stack.update_yaxes(gridcolor=GRID_COL)
            st.plotly_chart(fig_src_stack, use_container_width=True)

        # Treemap of source x label
        src_label_df = df.groupby(["source","primary_label"]).size().reset_index(name="count")
        if not src_label_df.empty:
            fig_tree = px.treemap(
                src_label_df,
                path=["primary_label","source"],
                values="count",
                color="primary_label",
                color_discrete_map=LABEL_COLORS,
            )
            fig_tree.update_layout(
                paper_bgcolor=PAPER_BG,
                font=dict(color="#F1F5F9"),
                height=400,
                margin=dict(l=10, r=10, t=40, b=10),
                title=dict(text="Source x Label Treemap", font=dict(color="#F1F5F9")),
            )
            st.plotly_chart(fig_tree, use_container_width=True)

else:
    st.info("👈 Click **Fetch Latest News** or **Load Sample Dataset** in the sidebar to begin.")
    c1, c2, c3 = st.columns(3)
    c1.markdown("**₿ Multi-label Classification**\n\nClassifies each headline as bullish, bearish, regulatory, technical, or macro")
    c2.markdown("**🔥 Sentiment Heatmap**\n\nAverage label scores per crypto ticker with radar chart per coin")
    c3.markdown("**📡 Source Intelligence**\n\nSentiment profile per news source with stacked bars and treemap")

st.markdown("---")
st.markdown("""
<div class="footer">
    Stack: spaCy · Sentence Transformers · HuggingFace · Streamlit · Plotly &nbsp;·&nbsp;
    Data: CoinGecko · CryptoPanic &nbsp;·&nbsp;
    <a href="https://github.com/fahadamjad009/nlp3-crypto-financial-news-intelligence" style="color:#F7931A">GitHub ↗</a>
</div>
""", unsafe_allow_html=True)