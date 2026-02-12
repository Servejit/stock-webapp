import streamlit as st
import yfinance as yf
import pandas as pd
import time

st.set_page_config(page_title="📊 Live Stock P2L", layout="wide")
st.title("📊 Live Prices with P2L")

# ---------------- STOCK LIST ----------------
stocks = {
    "AMBUJACEM.NS": 492.12,
    "BAJAJFINSV.NS": 1867.22,
    "BAJAJHLDNG.NS": 10348.00,
    "BANKBARODA.NS": 269.82,
    "BEL.NS": 423.42,
    "BOSCHLTD.NS": 35024.00,
    "COALINDIA.NS": 411.97,
    "DRREDDY.NS": 1161.26,
    "FEDERALBNK.NS": 274.62,
    "FORTIS.NS": 808.54,
    "GAIL.NS": 157.01,
    "GRASIM.NS": 2699.44,
    "HDFCLIFE.NS": 695.06,
    "HINDALCO.NS": 917.39,
    "IDFCFIRSTB.NS": 81.71,
    "INDUSINDBK.NS": 890.53,
    "IRCTC.NS": 593.02,
    "IRFC.NS": 110.97,
    "ITC.NS": 300.49,
    "JINDALSTEL.NS": 1077.29,
    "JIOFIN.NS": 236.41,
    "LICI.NS": 784.51,
    "MARICO.NS": 704.76,
    "MARUTI.NS": 13987.71,
    "MUTHOOTFIN.NS": 3401.97,
    "NAUKRI.NS": 1115.80,
    "NHPC.NS": 74.56,
    "NMDC.NS": 78.03,
    "OBEROIRLTY.NS": 1421.86,
    "OFSS.NS": 7127.14,
    "OIL.NS": 470.64,
    "ONGC.NS": 246.98,
    "PIIND.NS": 2995.95,
    "PNB.NS": 117.56,
    "POLICYBZR.NS": 1408.77,
    "POWERGRID.NS": 248.75,
    "SBICARD.NS": 723.34,
    "SHREECEM.NS": 25979.45,
    "SOLARINDS.NS": 12796.70,
    "SUZLON.NS": 45.18,
    "TATAPOWER.NS": 346.66,
    "TATASTEEL.NS": 182.09,
    "TCS.NS": 2908.71,
    "TORNTPHARM.NS": 3889.26,
    "TRENT.NS": 3626.78,
    "ULTRACEMCO.NS": 12130.05,
    "VBL.NS": 434.42,
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

            # Format numbers as strings with 2 decimals
            rows.append([
                sym,
                f"{p2l:.2f}",
                f"{price:.2f}",
                f"{pct:.2f}",
                f"{stocks[sym]:.2f}",
                f"{open_:.2f}",
                f"{high:.2f}",
                f"{low:.2f}"
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
    try:
        return "color: red; font-weight: bold" if float(val) < 0 else "color: green; font-weight: bold"
    except:
        return ""

st.dataframe(df.style.applymap(highlight_p2l, subset=["P2L %"]), use_container_width=True, hide_index=True)

# ---------------- AUTO REFRESH ----------------
if auto:
    time.sleep(30)
    st.experimental_rerun()
