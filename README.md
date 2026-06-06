\# ₿ NLP3 — Crypto \& Financial News Intelligence



> Real-time crypto news pipeline — \*\*multi-label classification\*\*, \*\*ticker trend detection\*\*, \*\*market sentiment scoring\*\*, \*\*radar charts\*\*, \*\*heatmaps\*\*, and \*\*source intelligence\*\* — powered by rule-based NLP, spaCy, and Plotly.



!\[Python](https://img.shields.io/badge/Python-3.11-3776AB?style=flat\&logo=python\&logoColor=white)

!\[spaCy](https://img.shields.io/badge/spaCy-3.8-09A3D5?style=flat\&logo=spacy\&logoColor=white)

!\[Streamlit](https://img.shields.io/badge/Streamlit-1.58-FF4B4B?style=flat\&logo=streamlit\&logoColor=white)

!\[Plotly](https://img.shields.io/badge/Plotly-Interactive-3F4F75?style=flat\&logo=plotly\&logoColor=white)

!\[HuggingFace](https://img.shields.io/badge/HuggingFace-Transformers-FFD21E?style=flat\&logo=huggingface\&logoColor=black)

!\[License](https://img.shields.io/badge/license-MIT-green)



\### \[▶ View Live App on Streamlit Cloud](https://nlp3-crypto-financial-news-intelligence.streamlit.app)



\---



\## Why this project



Most crypto sentiment tools are single-label and static. This project builds a real-time multi-label news intelligence pipeline — ingesting live crypto news from CoinGecko and CryptoPanic, classifying each headline across five dimensions simultaneously (bullish, bearish, regulatory, technical, macro), tagging crypto tickers and exchanges, computing a composite market sentiment score, and surfacing everything through a 5-tab interactive Streamlit dashboard with radar charts, heatmaps, and treemaps.



\*\*Target use case:\*\* Crypto trading desks, FinTech analysts, regulatory monitoring, portfolio risk dashboards, algorithmic trading signal generation.



\---



\## Live Demo



Five-tab interactive dashboard with sidebar label filters and live news refresh:



| Tab | What it shows |

|---|---|

| \*\*📊 Market Overview\*\* | Market sentiment gauge (0–100) · Label distribution donut · Articles per label bar · Score distribution box plot |

| \*\*📰 News Feed\*\* | Searchable + sortable live news feed · Colour-coded cards by label · Ticker tags · Full data table |

| \*\*₿ Ticker Analysis\*\* | Ticker mention frequency bar · Ticker coverage pie · Stacked sentiment per ticker · Bullish vs bearish scatter per coin |

| \*\*🔥 Trend Heatmap\*\* | Ticker × label sentiment heatmap · Interactive radar chart per coin · Multi-label distribution bar |

| \*\*📡 Source Intelligence\*\* | Articles per source bar · Source share pie · Sentiment breakdown per source · Source × label treemap |



\---



\## All components



| Component | File | What it does |

|---|---|---|

| News fetcher | `src/news\_fetcher.py` | CoinGecko + CryptoPanic APIs, sample fallback, ticker/exchange/macro tagging |

| Classifier | `src/classifier.py` | Rule-based multi-label classifier across 5 dimensions, zero-shot fallback |

| Trend detector | `src/trend\_detector.py` | Label distribution, ticker sentiment, market score, heatmap, source breakdown |

| Dashboard | `app.py` | 5-tab Streamlit app — gauge, feed, ticker, heatmap, radar, treemap |



\---



\## NLP skills demonstrated



| Skill | Where | Interview talking point |

|---|---|---|

| \*\*Multi-label classification\*\* | `classifier.py` | "Each headline can be bullish AND regulatory simultaneously — single-label misses this" |

| \*\*Rule-based NLP\*\* | `classifier.py` — keyword scoring | "Domain-specific lexicons outperform general models on financial text — fast and interpretable" |

| \*\*Named entity recognition\*\* | `news\_fetcher.py` — ticker/exchange tagging | "Regex + dictionary lookup for financial entities — production pattern in trading systems" |

| \*\*Real-time data ingestion\*\* | `news\_fetcher.py` — CoinGecko API | "REST API polling with graceful fallback — production-grade reliability pattern" |

| \*\*Sentiment scoring\*\* | `trend\_detector.py` — composite score | "Bullish/bearish ratio normalised to 0–100 — interpretable market signal" |

| \*\*Radar chart\*\* | Tab 4 — Plotly Scatterpolar | "Multi-axis sentiment fingerprint per ticker — shows dimension balance at a glance" |

| \*\*Heatmap\*\* | Tab 4 — Plotly Heatmap | "Ticker × label matrix — surfaces which coins dominate each sentiment dimension" |

| \*\*Treemap\*\* | Tab 5 — Plotly Treemap | "Source × label hierarchy — reveals editorial bias per news outlet" |

| \*\*Interactive filters\*\* | Sidebar multiselect | "Session-state filtering without re-fetching — Streamlit's st.session\_state pattern" |

| \*\*API fallback design\*\* | `news\_fetcher.py` | "Sample dataset fallback ensures demo reliability regardless of API status" |



\---



\## Dataset



Live news from two public APIs with sample fallback:



| Source | Type | Articles |

|---|---|---|

| CoinGecko News API | Live crypto news | Up to 30 per fetch |

| CryptoPanic Public Feed | Live crypto news | Up to 30 per fetch |

| Sample fallback | 25 curated headlines | Always available |



\*\*12 crypto tickers tracked:\*\* BTC, ETH, BNB, SOL, XRP, ADA, AVAX, DOGE, DOT, MATIC, LINK, UNI



\*\*5 classification labels:\*\* bullish · bearish · regulatory · technical · macro



\---



\## Project structure

nlp3-crypto-financial-news-intelligence/

├── app.py                        5-tab Streamlit dashboard

├── src/

│   ├── news\_fetcher.py           API ingestion + ticker/exchange/macro tagging

│   ├── classifier.py             Multi-label rule-based + zero-shot classifier

│   └── trend\_detector.py         Label distribution, ticker sentiment, market score

├── data/

│   ├── raw\_news.csv              Fetched + tagged news articles

│   ├── classified\_news.csv       Classified articles with label scores

│   └── sentiment\_heatmap.csv     Ticker × label average scores

├── tests/

│   └── test\_pipeline.py          Unit tests for classifier and trend detector

├── .streamlit/

│   └── config.toml               Dark orange Bitcoin theme

├── requirements.txt

├── packages.txt

└── .gitignore



\---



\## Local setup



```bash

git clone https://github.com/fahadamjad009/nlp3-crypto-financial-news-intelligence.git

cd nlp3-crypto-financial-news-intelligence

python -m venv venv

venv\\Scripts\\activate

pip install -r requirements.txt

python -m spacy download en\_core\_web\_sm

```



\*\*Run the pipeline:\*\*



```bash

python src/news\_fetcher.py

python src/classifier.py

python src/trend\_detector.py

```



\*\*Run the app:\*\*



```bash

streamlit run app.py

```



\---



\## Tech stack



Python · spaCy · HuggingFace Transformers · Sentence Transformers · Streamlit · Plotly · pandas · scikit-learn · requests · CoinGecko API · CryptoPanic API



\---





\---



\## License



MIT — see `LICENSE`

