# ---------------------------------------------------
# INSTALL
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

BOT_TOKEN = "YOUR_BOT_TOKEN"
CHAT_ID = "YOUR_CHAT_ID"

# ---------------------------------------------------
# FLASH CSS

st.markdown("""
<style>
@keyframes flash {
0% {opacity:1;}
50% {opacity:0.2;}
100% {opacity:1;}
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
s.strip().replace(".NS","")
for s in stockstar_input.split(",")
if s.strip()
]

# ---------------------------------------------------
# SOUND SETTINGS

sound_alert = st.toggle("🔊 Enable Sound Alert", False)

telegram_alert = st.toggle("📲 Enable Telegram Alert", False)

uploaded_sound = st.file_uploader(
"Upload Sound",
type=["mp3","wav"]
)

DEFAULT_SOUND_URL = "https://assets.mixkit.co/active_storage/sfx/2869/2869-preview.mp3"

# ---------------------------------------------------
# STOCK LIST

stocks = {

"ADANIENT.NS":2092.68,
"ADANIPORTS.NS":1487.82,
"AXISBANK.NS":1309.52,
"BHEL.NS":251.74,
"BOSCHLTD.NS":35043.90,
"BSE.NS":2718.29,
"CANBK.NS":139.45,
"COALINDIA.NS":404.57,
"DLF.NS":620.45,
"GMRAIRPORT.NS":93.06,
"HCLTECH.NS":1392.51,
"HDFCBANK.NS":896.50,
"HEROMOTOCO.NS":5419.27,
"HINDALCO.NS":878.80,
"HINDZINC.NS":573.56,
"IDFCFIRSTB.NS":79.61,
"INFY.NS":1278.30,
"IRCTC.NS":603.12,
"IRFC.NS":110.02,
"JSWENERGY.NS":466.51,
"M&M.NS":3444.69,
"MPHASIS.NS":2349.31,
"MUTHOOTFIN.NS":3431.50,
"NHPC.NS":74.28,
"OIL.NS":451.02,
"PFC.NS":395.26,
"PIIND.NS":2999.93,
"PNB.NS":116.96,
"POLYCAB.NS":7498.32,
"RECLTD.NS":338.10,
"RELIANCE.NS":1402.25,
"SRF.NS":2682.32,
"SUZLON.NS":45.11,
"TATACONSUM.NS":1111.51,
"TATASTEEL.NS":199.55,
"TCS.NS":2578.54,
"UPL.NS":712.82,
"YESBANK.NS":20.60,

}

# ---------------------------------------------------
# FETCH DATA

@st.cache_data(ttl=60)
def fetch_data():

    symbols = list(stocks.keys())

    daily = yf.download(
        tickers=symbols,
        period="2d",
        interval="1d",
        group_by="ticker",
        progress=False
    )

    intraday = yf.download(
        tickers=symbols,
        period="1d",
        interval="1m",
        group_by="ticker",
        progress=False
    )

    rows = []

    for sym in symbols:

        try:

            ref_low = stocks[sym]

            price = daily[sym]["Close"].iloc[-1]
            prev_close = daily[sym]["Close"].iloc[-2]

            open_p = daily[sym]["Open"].iloc[-1]
            high = daily[sym]["High"].iloc[-1]
            low = daily[sym]["Low"].iloc[-1]

            # DOWN MINUTES

            minutes_down = 0

            intraday_prices = intraday[sym]["Close"]

            below = intraday_prices[intraday_prices < ref_low]

            if not below.empty:

                first = below.index[0]
                now = intraday_prices.index[-1]

                minutes_down = int((now-first).total_seconds()/60)

            p2l = ((price-ref_low)/ref_low)*100
            pct_chg = ((price-prev_close)/prev_close)*100

            rows.append({

                "Stock": sym.replace(".NS",""),
                "P2L %": p2l,
                "Price": price,
                "Down Minutes": minutes_down,
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
# BUTTONS

col1,col2 = st.columns(2)

with col1:

    if st.button("Refresh"):

        st.cache_data.clear()
        st.rerun()

with col2:

    sort_clicked = st.button("Sort")

# ---------------------------------------------------

df = fetch_data()

numeric_cols = ["P2L %","Price","Down Minutes","% Chg","Low Price","Open","High","Low"]

for col in numeric_cols:

    df[col] = pd.to_numeric(df[col], errors="coerce")

# ---------------------------------------------------
# TABLE

def generate_html_table(dataframe):

    html = "<table style='width:100%;border-collapse:collapse;'>"

    html += "<tr style='background-color:#111;'>"

    for col in dataframe.columns:

        html += f"<th style='padding:8px;border:1px solid #444;'>{col}</th>"

    html += "</tr>"

    for _,row in dataframe.iterrows():

        html += "<tr>"

        for col in dataframe.columns:

            value = row[col]

            style="padding:6px;border:1px solid #444;text-align:center;"

            if col=="Down Minutes":

                mins=int(value)

                if mins<15 and mins>0:

                    value=f"🟠{mins}"
                    style+="color:orange;font-weight:bold;"

                else:

                    value=str(mins)

            if isinstance(value,float):

                value=f"{value:.2f}"

            html+=f"<td style='{style}'>{value}</td>"

        html+="</tr>"

    html+="</table>"

    return html

st.markdown(generate_html_table(df), unsafe_allow_html=True)

# ---------------------------------------------------
# AVERAGE

avg = df["P2L %"].mean()

st.markdown(f"### 📊 Average P2L of All Stocks is **{avg:.2f}%**")
