# ---------------------------------------------------
# INSTALL FIRST
# pip install streamlit yfinance pandas requests
# ---------------------------------------------------

import streamlit as st
import yfinance as yf
import pandas as pd
import requests
import time

st.set_page_config(layout="wide")

st.title("📉 Live Stock Monitor")

# ---------------------------------------------------
# TELEGRAM SETTINGS
# ---------------------------------------------------

BOT_TOKEN = "YOUR_BOT_TOKEN"
CHAT_ID = "YOUR_CHAT_ID"

def send_telegram(msg):

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    requests.post(url, data={
        "chat_id": CHAT_ID,
        "text": msg
    })


# ---------------------------------------------------
# STOCK LIST
# ---------------------------------------------------

stocks = {

"RELIANCE.NS": 2900,
"HDFCBANK.NS": 1500,
"INFY.NS": 1400,
"ICICIBANK.NS": 1000,
"TCS.NS": 3500,

}

# ---------------------------------------------------
# FETCH DATA
# ---------------------------------------------------

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

            prev = daily[sym]["Close"].iloc[-2]

            open_p = daily[sym]["Open"].iloc[-1]

            high = daily[sym]["High"].iloc[-1]

            low = daily[sym]["Low"].iloc[-1]

            # ---------------------------------
            # DOWN MINUTES ONLY IF BELOW LOW
            # ---------------------------------

            minutes_down = ""

            intraday_prices = intraday[sym]["Close"]

            below = intraday_prices[intraday_prices < ref_low]

            if not below.empty:

                first = below.index[0]

                now = intraday_prices.index[-1]

                minutes_down = int(
                    (now - first).total_seconds()/60
                )

            # ---------------------------------

            p2l = ((price-ref_low)/ref_low)*100

            chg = ((price-prev)/prev)*100

            rows.append({

                "Stock": sym.replace(".NS",""),

                "Price": price,

                "Low Price": ref_low,

                "Down Minutes": minutes_down,

                "P2L %": p2l,

                "% Chg": chg,

                "Open": open_p,

                "High": high,

                "Low": low

            })

        except:

            pass


    return pd.DataFrame(rows)


df = fetch_data()


# ---------------------------------------------------
# HTML TABLE
# ---------------------------------------------------

def generate_html(df):

    html = """

    <style>

    @keyframes flash {

    0% {opacity:1;}

    50% {opacity:0.3;}

    100% {opacity:1;}

    }

    </style>

    <table style="width:100%; border-collapse: collapse;">

    <tr style="background:black; color:white;">

    """

    for col in df.columns:

        html += f"<th style='padding:8px'>{col}</th>"


    html += "</tr>"


    for _,row in df.iterrows():

        html+="<tr>"


        for col in df.columns:

            val=row[col]

            style="padding:8px; text-align:center;"


            # -----------------------
            # ORANGE MINUTES ONLY
            # -----------------------

            if col=="Down Minutes":

                if val!="":

                    val=f"🟠 {val}"

                    style+="color:orange; font-weight:bold;"

                else:

                    val=""


            # PERCENT COLORS

            if col in ["P2L %","% Chg"]:

                if val>0:

                    style+="color:green;"

                elif val<0:

                    style+="color:red;"


            if isinstance(val,float):

                val=f"{val:.2f}"


            html+=f"<td style='{style}'>{val}</td>"


        html+="</tr>"


    html+="</table>"

    return html


st.markdown(generate_html(df),unsafe_allow_html=True)


# ---------------------------------------------------
# TELEGRAM ALERT
# ---------------------------------------------------

for i,row in df.iterrows():

    if row["Down Minutes"]!="":

        send_telegram(

            f"{row['Stock']} below Low 🔻\n"

            f"🟠 {row['Down Minutes']} minutes"

        )


# ---------------------------------------------------
# AUTO REFRESH
# ---------------------------------------------------

time.sleep(60)

st.rerun()
