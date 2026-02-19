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
"⭐ StockStar",
"BOSCHLTD.NS, BSE.NS, HEROMOTOCO.NS, HINDALCO.NS, HINDZINC.NS, M&M.NS, MUTHOOTFIN.NS, PIIND.NS"
).upper()

stockstar_list = [
s.strip().replace(".NS","")
for s in stockstar_input.split(",")
if s.strip()
]

# ---------------------------------------------------
# SOUND

sound_alert = st.toggle("🔊 Sound Alert", False)

telegram_alert = st.toggle("📲 Telegram Alert", False)

uploaded_sound = st.file_uploader(
"Upload Sound",
type=["mp3","wav"]
)

DEFAULT_SOUND_URL = "https://assets.mixkit.co/active_storage/sfx/2869/2869-preview.mp3"

# ---------------------------------------------------
# STOCK LIST

stocks = {

"BOSCHLTD.NS":35043.90,
"BSE.NS":2718.29,
"HEROMOTOCO.NS":5419.27,
"HINDALCO.NS":878.80,
"HINDZINC.NS":573.56,
"M&M.NS":3444.69,
"MUTHOOTFIN.NS":3431.50,
"PIIND.NS":2999.93,
"RELIANCE.NS":1402.25,
"TCS.NS":2578.54,
"INFY.NS":1278.30,
"HDFCBANK.NS":896.50,

}

# ---------------------------------------------------
# FETCH DATA

@st.cache_data(ttl=60)
def fetch_data():

symbols=list(stocks.keys())

daily=yf.download(
tickers=symbols,
period="2d",
interval="1d",
group_by="ticker",
progress=False
)

intraday=yf.download(
tickers=symbols,
period="1d",
interval="1m",
group_by="ticker",
progress=False
)

rows=[]

for sym in symbols:

try:

ref_low=stocks[sym]

price=daily[sym]["Close"].iloc[-1]
prev_close=daily[sym]["Close"].iloc[-2]

open_p=daily[sym]["Open"].iloc[-1]
high=daily[sym]["High"].iloc[-1]
low=daily[sym]["Low"].iloc[-1]

# --------------------
# DOWN MINUTES
# --------------------

minutes_down=0

intraday_prices=intraday[sym]["Close"]

below=intraday_prices[intraday_prices<ref_low]

if not below.empty:

first=below.index[0]
now=intraday_prices.index[-1]

minutes_down=int(
(now-first).total_seconds()/60
)

# --------------------

p2l=((price-ref_low)/ref_low)*100

pct_chg=((price-prev_close)/prev_close)*100

rows.append({

"Stock":sym.replace(".NS",""),

"P2L %":p2l,

"Price":price,

"Down Minutes":minutes_down,

"% Chg":pct_chg,

"Low Price":ref_low,

"Open":open_p,

"High":high,

"Low":low

})

except:
pass

return pd.DataFrame(rows)

# ---------------------------------------------------
# BUTTONS

col1,col2=st.columns(2)

with col1:

if st.button("🔄 Refresh"):

st.cache_data.clear()

st.rerun()

with col2:

sort_clicked=st.button("📈 Sort")

# ---------------------------------------------------
# LOAD

df=fetch_data()

if df.empty:

st.error("No data")

st.stop()

numeric_cols=[

"P2L %",
"Price",
"Down Minutes",
"% Chg",
"Low Price",
"Open",
"High",
"Low"

]

for col in numeric_cols:

df[col]=pd.to_numeric(df[col],errors="coerce")

if sort_clicked:

df=df.sort_values("P2L %",ascending=False)

# ---------------------------------------------------
# TELEGRAM TRIGGER

green_trigger=False

trigger_stock=""
trigger_price=0
trigger_p2l=0

for _,row in df.iterrows():

if row["Stock"] in stockstar_list and row["P2L %"]<-5:

green_trigger=True

trigger_stock=row["Stock"]

trigger_price=row["Price"]

trigger_p2l=row["P2L %"]

break

# ---------------------------------------------------
# SESSION

if "alert_played" not in st.session_state:

st.session_state.alert_played=False

if not green_trigger:

st.session_state.alert_played=False

# ---------------------------------------------------
# TELEGRAM

if telegram_alert and green_trigger and not st.session_state.alert_played:

time=datetime.now().strftime("%I:%M:%S %p")

msg=f"""

🟢 GREEN ALERT

{trigger_stock}

₹{trigger_price:.2f}

{trigger_p2l:.2f}%

{time}

"""

url=f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

requests.post(url,data={

"chat_id":CHAT_ID,

"text":msg

})

# ---------------------------------------------------
# HTML TABLE

def generate_html_table(dataframe):

html="""

<table style="width:100%;border-collapse:collapse;">

<tr style="background-color:#111;">

"""

for col in dataframe.columns:

html+=f"<th style='padding:8px;border:1px solid #444;'>{col}</th>"

html+="</tr>"

for _,row in dataframe.iterrows():

html+="<tr>"

for col in dataframe.columns:

value=row[col]

style="padding:6px;border:1px solid #444;text-align:center;"

# DOWN MINUTES ORANGE

if col=="Down Minutes":

mins=int(value)

if mins<15 and mins>0:

value=f"🟠{mins}"

style+="color:orange;font-weight:bold;"

else:

value=str(mins)

# STOCK FLASH

if col=="Stock":

if row["Stock"] in stockstar_list and row["P2L %"]<-5:

style+="color:green;font-weight:bold;animation:flash 1s infinite;"

# PERCENT COLORS

if col in ["P2L %","% Chg"]:

if row[col]>0:

style+="color:green;font-weight:bold;"

elif row[col]<0:

style+="color:red;font-weight:bold;"

# FLOAT FORMAT

if isinstance(value,float):

value=f"{value:.2f}"

html+=f"<td style='{style}'>{value}</td>"

html+="</tr>"

html+="</table>"

return html

st.markdown(generate_html_table(df),unsafe_allow_html=True)

# ---------------------------------------------------
# SOUND

if sound_alert and green_trigger and not st.session_state.alert_played:

st.session_state.alert_played=True

if uploaded_sound:

audio_bytes=uploaded_sound.read()

b64=base64.b64encode(audio_bytes).decode()

st.markdown(f"""

<audio autoplay>

<source src="data:audio/mp3;base64,{b64}">

</audio>

""",unsafe_allow_html=True)

else:

st.markdown(f"""

<audio autoplay>

<source src="{DEFAULT_SOUND_URL}">

</audio>

""",unsafe_allow_html=True)

# ---------------------------------------------------
# AVERAGE

avg=df["P2L %"].mean()

st.markdown(f"### Average P2L : {avg:.2f}%")
