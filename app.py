import streamlit as st
import yfinance as yf
import pandas as pd
import time

st.set_page_config(page_title="📊 Live Stock P2L", layout="wide")
st.title("📊 Live Prices with P2L")

# ---------------- STOCK LIST ----------------
stocks = {
    "AMBUJACEM": 492.12, "BAJAJFINSV": 1867.22, "BAJAJHLDNG": 10348.00, "BANKBARODA": 269.82,
    "COALINDIA": 411.97, "DRREDDY": 1161.26, "FEDERALBNK": 274.62, "FORTIS": 808.54,
    "GAIL": 157.01, "GRASIM": 2699.44, "IRCTC": 593.02, "IRFC": 110.97, "ITC": 300.49,
    "JINDALSTEL": 1077.29, "JIOFIN": 236.41, "LICI": 784.51, "MARICO": 704.76,
    "MARUTI": 13987.71, "MUTHOOTFIN": 3401.97, "NAUKRI": 1145.84, "NHPC": 74.56,
    "NMDC": 78.03, "OBEROIRLTY": 1421.86, "OFSS": 7372.95, "ONGC": 246.98,
    "PIIND": 2995.95, "PNB": 117.56, "POLICYBZR": 1405.24, "POWERGRID": 248.75,
    "SBICARD": 723.34, "SHREECEM": 25979.45, "SUZLON": 45.18, "TATAPOWER": 346.66,
    "TATASTEEL": 182.09, "TRENT": 3626.78, "ULTRACEMCO": 12130.05, "VBL": 434.42
}

symbols = [s + ".NS" for s in stocks.keys()]

# ---------------- FETCH DATA ----------------
@st.cache_data(ttl=20)
def fetch_data():
    df = yf.download(symbols, period="1d", interval="1m", progress=False)
    rows = []

    for sym in stocks:
        try:
            s = sym + ".NS"
            price = df["Close"][s].iloc[-1]
            open_ = df["Open"][s].iloc[-1]
            high = df["High"][s].iloc[-1]
            low = df["Low"][s].iloc[-1]

            pct = ((price - open_) / open_) * 100
            p2l = ((price - stocks[sym]) / stocks[sym]) * 100

            rows.append([
                sym,
                round(p2l, 2),
                round(price, 2),
                round(pct, 2),
                round(stocks[sym], 2),
                round(open_, 2),
                round(high, 2),
                round(low, 2)
            ])
        except Exception as e:
            print(f"Error fetching {sym}: {e}")
            continue

    return pd.DataFrame(
        rows,
        columns=["Stock", "P2L %", "Price", "% Chg", "Low Price", "Open", "High", "Low"]
    )

# ---------------- BUTTONS ----------------
c1, c2, c3 = st.columns([1,1,1])
with c1:
    refresh = st.button("🔄 Refresh")
with c2:
    sortp = st.button("📈 Sort P2L")
with c3:
    auto = st.checkbox("⏱ Auto Refresh 30s")

# ---------------- DATA ----------------
df = fetch_data()
if sortp:
    df = df.sort_values("P2L %", ascending=False)

# Conditional styling: P2L negative in red
def highlight_p2l(val):
    color = "red" if val < 0 else "green"
    return f"color: {color}; font-weight: bold"

st.dataframe(df.style.applymap(highlight_p2l, subset=["P2L %"]), use_container_width=True, hide_index=True)

# ---------------- AUTO REFRESH ----------------
if auto:
    time.sleep(30)
    st.experimental_rerun()
