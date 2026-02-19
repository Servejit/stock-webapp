# ---------------------------------------------------
# INSTALL (Run once in terminal)
# pip install streamlit yfinance pandas requests
# ---------------------------------------------------

import streamlit as st
import yfinance as yf
import pandas as pd
import base64
import requests
from datetime import datetime

st.set_page_config(page_title="📊 Live Stock P2L", layout="wide")
st.title("📊 Live Prices with P2L")

# ---------------------------------------------------
# TELEGRAM SETTINGS

BOT_TOKEN = "8371973661:AAFTOjh53yKmmgv3eXqD5wf8Ki6XXrZPq2c"
CHAT_ID = "5355913841"

# ---------------------------------------------------
# FLASHING CSS

st.markdown("""
<style>
@keyframes flash {
    0% { opacity: 1; }
    50% { opacity: 0.2; }
    100% { opacity: 1; }
}
table {
    background-color:#0e1117;
    color:white;
}
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------
# STOCKSTAR INPUT

stockstar_input = st.text_input(
    "⭐ StockStar (Comma Separated)",
    "BOSCHLTD.NS, BSE.NS, HEROMOTOCO.NS, HINDALCO.NS, HINDZINC.NS, M&M.NS, MUTHOOTFIN.NS, PIIND.NS"
).upper()

stockstar_list = [
    s.strip().replace(".NS", "")
    for s in stockstar_input.split(",")
    if s.strip() != ""
]

# ---------------------------------------------------
# SOUND SETTINGS

sound_alert = st.toggle("🔊 Enable Alert Sound for -5% Green Stocks", value=False)

# ---------------------------------------------------
# TELEGRAM ALERT TOGGLE

telegram_alert = st.toggle("📲 Enable Telegram Alert for Green Flashing", value=False)

# ---------------------------------------------------
# SOUND UPLOAD

st.markdown("### 🎵 Alert Sound Settings")

uploaded_sound = st.file_uploader(
    "Upload Your Custom Sound (.mp3 or .wav)",
    type=["mp3", "wav"]
)

DEFAULT_SOUND_URL = "https://assets.mixkit.co/active_storage/sfx/2869/2869-preview.mp3"

# ---------------------------------------------------
# STOCK LIST

stocks = {
    "ADANIENT.NS": 2092.68,
    "ADANIPORTS.NS": 1487.82,
    "AMBUJACEM.NS": 510.63,
    "AXISBANK.NS": 1309.52,
    "BAJAJHFL.NS": 88.23,
    "BHEL.NS": 251.74,
    "BOSCHLTD.NS": 35043.90,
    "BPCL.NS": 367.20,
    "BSE.NS": 2718.29,
    "CANBK.NS": 139.45,
    "COALINDIA.NS": 404.57,
    "COFORGE.NS": 1330.67,
    "DLF.NS": 620.45,
    "DMART.NS": 3823.09,
    "GMRAIRPORT.NS": 93.06,
    "GODREJCP.NS": 1165.94,
    "HCLTECH.NS": 1392.51,
    "HDFCBANK.NS": 896.50,
    "HEROMOTOCO.NS": 5419.27,
    "HINDALCO.NS": 878.80,
    "HINDUNILVR.NS": 2282.38,
    "HINDZINC.NS": 573.56,
    "IDFCFIRSTB.NS": 79.61,
    "INFY.NS": 1278.30,
    "IRCTC.NS": 603.12,
    "IRFC.NS": 110.02,
    "JIOFIN.NS": 258.25,
    "JSWENERGY.NS": 466.51,
    "JUBLFOOD.NS": 522.62,
    "KOTAKBANK.NS": 416.16,
    "LTIM.NS": 4975.53,
    "M&M.NS": 3444.69,
    "MPHASIS.NS": 2349.31,
    "MUTHOOTFIN.NS": 3431.50,
    "NAUKRI.NS": 1098.68,
    "NHPC.NS": 74.28,
    "OFSS.NS": 6384.00,
    "OIL.NS": 451.02,
    "PAGEIND.NS": 33063.85,
    "PERSISTENT.NS": 5196.98,
    "PFC.NS": 395.26,
    "PIIND.NS": 2999.93,
    "PNB.NS": 116.96,
    "POLYCAB.NS": 7498.32,
    "PRESTIGE.NS": 1474.69,
    "RECLTD.NS": 338.10,
    "RELIANCE.NS": 1402.25,
    "SHREECEM.NS": 25621.25,
    "SOLARINDS.NS": 12787.74,
    "SRF.NS": 2682.32,
    "SUZLON.NS": 45.11,
    "TATACONSUM.NS": 1111.51,
    "TATASTEEL.NS": 199.55,
    "TCS.NS": 2578.54,
    "UPL.NS": 712.82,
    "VBL.NS": 443.37,
    "YESBANK.NS": 20.60,
}

# ---------------------------------------------------
# FETCH DATA

@st.cache_data(ttl=60)
def fetch_data():

    symbols = list(stocks.keys())

    data = yf.download(
        tickers=symbols,
        period="2d",
        interval="1d",
        group_by="ticker",
        progress=False,
        threads=True
    )

    rows = []

    for sym in symbols:

        try:

            ref_low = stocks[sym]

            price = data[sym]["Close"].iloc[-1]
            prev_close = data[sym]["Close"].iloc[-2]
            open_p = data[sym]["Open"].iloc[-1]
            high = data[sym]["High"].iloc[-1]
            low = data[sym]["Low"].iloc[-1]

            p2l = ((price - ref_low) / ref_low) * 100
            pct_chg = ((price - prev_close) / prev_close) * 100

            rows.append({
                "Stock": sym.replace(".NS", ""),
                "P2L %": p2l,
                "Price": price,
                "% Chg": pct_chg,
                "Low Price": ref_low,
                "Open": open_p,
                "High": high,
                "Low": low
            })

        except:
            pass

    return pd.DataFrame(rows)

# ---------------------------------------------------
# LOAD DATA

df = fetch_data()

# ---------------------------------------------------
# DURATION TRACKING

if "trigger_times" not in st.session_state:
    st.session_state.trigger_times = {}

duration_list = []

now = datetime.now()

for _, row in df.iterrows():

    stock = row["Stock"]

    if stock in stockstar_list and row["P2L %"] < -5:

        if stock not in st.session_state.trigger_times:
            st.session_state.trigger_times[stock] = now

        minutes = int((now - st.session_state.trigger_times[stock]).total_seconds() / 60)

        duration_list.append(minutes)

    else:

        duration_list.append("")

# INSERT AFTER PRICE COLUMN

price_index = df.columns.get_loc("Price")
df.insert(price_index + 1, "Duration", duration_list)

# ---------------------------------------------------
# HTML TABLE

def generate_html_table(dataframe):

    html = """<table style="width:100%; border-collapse: collapse;"><tr style="background-color:#111;">"""

    for col in dataframe.columns:
        html += f"<th style='padding:8px; border:1px solid #444;'>{col}</th>"

    html += "</tr>"

    for _, row in dataframe.iterrows():

        html += "<tr>"

        for col in dataframe.columns:

            value = row[col]
            style = "padding:6px; border:1px solid #444; text-align:center;"

            # DURATION COLOR

            if col == "Duration" and value != "":

                if int(value) < 15:

                    value = f"🟠{value}"
                    style += "color:orange; font-weight:bold;"

            if isinstance(value, float):
                value = f"{value:.2f}"

            html += f"<td style='{style}'>{value}</td>"

        html += "</tr>"

    html += "</table>"

    return html

st.markdown(generate_html_table(df), unsafe_allow_html=True)

# ---------------------------------------------------
# AVERAGE

average_p2l = df["P2L %"].mean()

st.markdown(
    f"### 📊 Average P2L of All Stocks is **{average_p2l:.2f}%**"
)
