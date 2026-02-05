import streamlit as st
import yfinance as yf
import pandas as pd
import time

# ---------------- PAGE SETUP ----------------
st.set_page_config(
    page_title="Live Stock P2L Dashboard",
    layout="wide"
)

st.title("📊 Live Prices with P2L")

# ---------------- STOCK LIST ----------------

stocks = {
    "AMBUJACEM": 492.12,
    "BAJAJFINSV": 1867.22,
    "BAJAJHLDNG": 10348.00,
    "BANKBARODA": 269.82,
    "COALINDIA": 411.97,
    "DRREDDY": 1161.26,
    "FEDERALBNK": 274.62,
    "FORTIS": 808.54,
    "GAIL": 157.01,
    "GRASIM": 2699.44,
    "IRCTC": 593.02,
    "IRFC": 110.97,
    "ITC": 300.49,
    "JINDALSTEL": 1077.29,
    "JIOFIN": 236.41,
    "LICI": 784.51,
    "MARICO": 704.76,
    "MARUTI": 13987.71,
    "MUTHOOTFIN": 3401.97,
    "NAUKRI": 1145.84,
    "NHPC": 74.56,
    "NMDC": 78.03,
    "OBEROIRLTY": 1421.86,
    "OFSS": 7372.95,
    "ONGC": 246.98,
    "PIIND": 2995.95,
    "PNB": 117.56,
    "POLICYBZR": 1405.24,
    "POWERGRID": 248.75,
    "SBICARD": 723.34,
    "SHREECEM": 25979.45,
    "SUZLON": 45.18,
    "TATAPOWER": 346.66,
    "TATASTEEL": 182.09,
    "TRENT": 3626.78,
    "ULTRACEMCO": 12130.05,
    "VBL": 434.42
}

# ---------------- DATA FETCH ----------------

@st.cache_data(ttl=30)
def fetch_data():
    rows = []

    for sym, ref_low in stocks.items():
        try:
            symbol = sym + ".NS"
            t = yf.Ticker(symbol)
            info = t.info

            price = info.get("regularMarketPrice", 0)
            open_ = info.get("open", 0)
            high = info.get("dayHigh", 0)
            low = info.get("dayLow", 0)
            chg = info.get("regularMarketChangePercent", 0)

            p2l = ((price - ref_low) / ref_low) * 100 if ref_low else 0

            rows.append([
                info.get("shortName", sym),
                round(p2l,2),
                round(price,2),
                round(chg,2),
                round(ref_low,2),
                round(open_,2),
                round(high,2),
                round(low,2)
            ])
        except:
            pass

    return pd.DataFrame(
        rows,
        columns=["Stock","P2L %","Price","% Chg","Low Price","Open","High","Low"]
    )

# ---------------- STYLING ----------------

def style_df(df):

    def color_stock(val, p2l):
        return "color: hotpink" if p2l < 0 else "color: black"

    styled = df.style

    styled = styled.apply(
        lambda x: [
            color_stock(v, df.loc[i,"P2L %"]) if x.name=="Stock" else ""
            for i,v in enumerate(x)
        ],
        axis=0
    )

    for col in ["Open","High","Low"]:
        styled = styled.apply(
            lambda x: ["color: hotpink"]*len(x),
            subset=[col]
        )

    styled = styled.format("{:.2f}", subset=df.select_dtypes("number").columns)

    styled = styled.set_properties(**{"font-size":"11px"})

    return styled

# ---------------- BUTTONS TOP ----------------

col1, col2, col3 = st.columns(3)

with col1:
    refresh_btn = st.button("🔄 Refresh")

with col2:
    sort_btn = st.button("📈 Sort P2L")

with col3:
    auto = st.toggle("⏱ Auto Refresh 30s")

# ---------------- DATA LOAD ----------------

df = fetch_data()

if sort_btn:
    df = df.sort_values("P2L %", ascending=False)

# ---------------- DISPLAY ----------------

st.dataframe(
    style_df(df),
    use_container_width=True,
    hide_index=True
)

# ---------------- BUTTONS BOTTOM ----------------

col4, col5 = st.columns(2)

with col4:
    st.button("🔄 Refresh ")

with col5:
    st.button("📈 Sort P2L ")

# ---------------- AUTO REFRESH ----------------

if auto:
    time.sleep(30)
    st.experimental_rerun()
  
