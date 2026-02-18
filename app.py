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

BOT_TOKEN = "8371973661:AAFTOjh53yKmmgv3eXqD5wf8Ki6XXrZPq2c"
CHAT_ID = "5355913841"

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
"⭐ StockStar",
"BOSCHLTD.NS, BSE.NS, HEROMOTOCO.NS, HINDALCO.NS, ITC.NS"
).upper()

stockstar_list = [
s.strip().replace(".NS","")
for s in stockstar_input.split(",")
if s.strip()
]

# ---------------------------------------------------
# TOGGLES

sound_alert = st.toggle("🔊 Sound Alert")

telegram_alert = st.toggle("📲 Telegram Alert")

# ---------------------------------------------------
# SOUND

uploaded_sound = st.file_uploader("Upload Sound")

DEFAULT_SOUND_URL = "https://assets.mixkit.co/active_storage/sfx/2869/2869-preview.mp3"

# ---------------------------------------------------
# STOCK LIST

stocks = {

"BOSCHLTD.NS":35043.90,
"BSE.NS":2718.29,
"HEROMOTOCO.NS":5419.27,
"HINDALCO.NS":878.80,
"ITC.NS":375.49,

}

# ---------------------------------------------------
# DOWN SINCE FUNCTION

@st.cache_data(ttl=60)
def down_since(symbol, ref, price):

    try:

        if price >= ref:
            return 0

        data = yf.download(symbol, period="1d", interval="1m", progress=False)

        closes = data["Close"]

        now = closes.index[-1]

        start=None

        for t,p in reversed(closes.items()):

            if p>=ref:
                break

            start=t

        if start:

            return int((now-start).total_seconds()/60)

        return 0

    except:

        return 0


# ---------------------------------------------------
# FETCH

@st.cache_data(ttl=60)
def fetch():

    rows=[]

    data=yf.download(

    tickers=list(stocks.keys()),
    period="2d",
    interval="1d",
    group_by="ticker",
    progress=False

    )

    for s in stocks:

        try:

            ref=stocks[s]

            price=data[s]["Close"].iloc[-1]

            prev=data[s]["Close"].iloc[-2]

            openp=data[s]["Open"].iloc[-1]

            high=data[s]["High"].iloc[-1]

            low=data[s]["Low"].iloc[-1]

            p2l=((price-ref)/ref)*100

            chg=((price-prev)/prev)*100

            mins=down_since(s,ref,price)

            rows.append({

            "Stock":s.replace(".NS",""),

            "P2L %":p2l,

            "Price":price,

            "Down Since":mins,

            "% Chg":chg,

            "Low Price":ref,

            "Open":openp,

            "High":high,

            "Low":low

            })

        except:

            pass

    return pd.DataFrame(rows)

# ---------------------------------------------------
# REFRESH

if st.button("🔄 Refresh"):

    st.cache_data.clear()

    st.rerun()

# ---------------------------------------------------
# LOAD

df=fetch()

# ---------------------------------------------------
# GREEN CHECK

green=False

for _,r in df.iterrows():

    if r["Stock"] in stockstar_list and r["P2L %"]<-5:

        green=True

        gstock=r["Stock"]

        gprice=r["Price"]

        gp2l=r["P2L %"]

        break

# ---------------------------------------------------
# TELEGRAM FIX

if telegram_alert and green:

    if "telegram" not in st.session_state:

        st.session_state.telegram=False

    if not st.session_state.telegram:

        msg=f"""

GREEN ALERT

Stock: {gstock}

Price: {gprice:.2f}

P2L: {gp2l:.2f}

Time: {datetime.now()}

"""

        url=f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

        res=requests.post(url,data={"chat_id":CHAT_ID,"text":msg})

        if res.status_code==200:

            st.session_state.telegram=True

else:

    st.session_state.telegram=False

# ---------------------------------------------------
# SOUND FIX

if sound_alert and green:

    if "sound" not in st.session_state:

        st.session_state.sound=False

    if not st.session_state.sound:

        st.session_state.sound=True

        if uploaded_sound:

            st.audio(uploaded_sound, autoplay=True)

        else:

            st.audio(DEFAULT_SOUND_URL, autoplay=True)

else:

    st.session_state.sound=False

# ---------------------------------------------------
# HTML TABLE

def table(d):

    html="<table border=1><tr>"

    for c in d.columns:

        html+=f"<th>{c}</th>"

    html+="</tr>"

    for _,r in d.iterrows():

        html+="<tr>"

        for c in d.columns:

            style=""

            if c=="Down Since":

                style="color:orange;font-weight:bold;"

            if c=="Stock" and r["Stock"] in stockstar_list and r["P2L %"]<-5:

                style="color:green;animation:flash 1s infinite;"

            html+=f"<td style='{style}'>{round(r[c],2) if isinstance(r[c],float) else r[c]}</td>"

        html+="</tr>"

    html+="</table>"

    return html

st.markdown(table(df), unsafe_allow_html=True)

# ---------------------------------------------------
# AVERAGE

st.write("Average:",round(df["P2L %"].mean(),2))
