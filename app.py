# -----------------------------------------
# INSTALL (Run once in terminal)
# pip install streamlit yfinance pandas
# -----------------------------------------

import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(page_title="📊 Live Stock P2L", layout="wide")
st.title("📊 Live Prices with P2L")

# -----------------------------------
# UPDATED STOCK LIST (Stock : Reference Low Price)

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

# -----------------------------------
# FUNCTION TO FETCH DATA

@st.cache_data(ttl=60)
def fetch_data():
    rows = []

    for sym, ref_low in stocks.items():
        try:
            t = yf.Ticker(sym)
            info = t.info

            price = info.get("regularMarketPrice", 0)
            change_percent = info.get("regularMarketChangePercent", 0)

            if price:
                p2l = ((price - ref_low) / ref_low) * 100
            else:
                p2l = 0

            rows.append({
                "Stock": info.get("shortName", sym.replace(".NS", "")),
                "P2L %": p2l,
                "Price": price,
                "% Chg": change_percent,
                "Low Price": ref_low,
                "Open": info.get("open", 0),
                "High": info.get("dayHigh", 0),
                "Low": info.get("dayLow", 0)
            })

        except:
            pass

    return pd.DataFrame(rows)

# -----------------------------------
# BUTTONS

col1, col2 = st.columns(2)

with col1:
    if st.button("🔄 Refresh"):
        st.cache_data.clear()

with col2:
    sort_clicked = st.button("📈 Sort by P2L")

# -----------------------------------
# LOAD DATA

df = fetch_data()

if sort_clicked:
    df = df.sort_values("P2L %", ascending=False)

# -----------------------------------
# STYLING FUNCTION

def color_rows(row):
    style = []

    # Stock name pink if P2L negative
    if row["P2L %"] < 0:
        style.append("color: hotpink")
    else:
        style.append("color: black")

    # Remaining columns
    for col in row.index[1:]:
        if col in ["Open", "High", "Low"]:
            style.append("color: hotpink")
        else:
            style.append("color: black")

    return style

# Apply styling
styled_df = df.style.apply(color_rows, axis=1).format("{:.2f}")

st.dataframe(styled_df, use_container_width=True)
