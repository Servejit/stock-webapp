import streamlit as st
import yfinance as yf
import pandas as pd
import time

st.set_page_config(page_title="📊 Live Stock P2L", layout="wide")
st.title("📊 Live Prices with P2L")

# ---------------- STOCK LIST ----------------
stocks = {
    "CANBK.NS": 142.93,
    "CHOLAFIN.NS": 1690.51,
    "COALINDIA.NS": 414.07,
    "DLF.NS": 646.85,
    "HCLTECH.NS": 1465.83,
    "IDFCFIRSTB.NS": 80.84,
    "INFY.NS": 1377.05,
    "MPHASIS.NS": 2445.51,
    "NHPC.NS": 75.78,
    "OIL.NS": 468.65,
    "PAGEIND.NS": 33501.65,
    "PERSISTENT.NS": 5417.42,
    "PNB.NS": 119.90,
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
