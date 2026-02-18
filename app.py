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
# SOUND TOGGLE

sound_alert = st.toggle("🔊 Enable Alert Sound for -5% Green Stocks", value=False)

# ---------------------------------------------------
# TELEGRAM TOGGLE

telegram_alert = st.toggle("📲 Enable Telegram Alert for Green Flashing", value=False)

# ---------------------------------------------------
# SOUND UPLOAD

uploaded_sound = st.file_uploader(
"Upload Your Custom Sound (.mp3 or .wav)",
type=["mp3", "wav"]
)

DEFAULT_SOUND_URL = "https://assets.mixkit.co/active_storage/sfx/2869/2869-preview.mp3"

# ---------------------------------------------------
# STOCK LIST (SAME)

stocks = {
"BOSCHLTD.NS": 35043.90,
"BSE.NS": 2718.29,
"HEROMOTOCO.NS": 5419.27,
"HINDALCO.NS": 878.80,
"HINDZINC.NS": 573.56,
"M&M.NS": 3444.69,
"MUTHOOTFIN.NS": 3431.50,
"PIIND.NS": 2999.93,
}

# ---------------------------------------------------
# FETCH DATA

@st.cache_data(ttl=60)
def fetch_data():

data = yf.download(
tickers=list(stocks.keys()),
period="2d",
interval="1d",
group_by="ticker",
progress=False
)

rows=[]

for sym in stocks:

try:

ref=stocks[sym]

price=data[sym]["Close"].iloc[-1]

prev=data[sym]["Close"].iloc[-2]

open_p=data[sym]["Open"].iloc[-1]

high=data[sym]["High"].iloc[-1]

low=data[sym]["Low"].iloc[-1]

p2l=((price-ref)/ref)*100

pct_chg=((price-prev)/prev)*100

rows.append({

"Stock": sym.replace(".NS",""),
"P2L %": p2l,
"Price": price,
"% Chg": pct_chg,
"Low Price": ref,
"Open": open_p,
"High": high,
"Low": low

})

except:
pass

return pd.DataFrame(rows)

# ---------------------------------------------------
# BUTTONS

if st.button("🔄 Refresh"):

st.cache_data.clear()
st.rerun()

# ---------------------------------------------------
# LOAD

df=fetch_data()

# ---------------------------------------------------
# GREEN TRIGGER CHECK

green_trigger=False

for _,row in df.iterrows():

if row["Stock"] in stockstar_list and row["P2L %"]<-5:

green_trigger=True
trigger_stock=row["Stock"]
trigger_price=row["Price"]
trigger_p2l=row["P2L %"]

break

# ---------------------------------------------------
# SESSION STATE INIT

if "telegram_sent" not in st.session_state:

st.session_state.telegram_sent=False

if "sound_sent" not in st.session_state:

st.session_state.sound_sent=False

# ---------------------------------------------------
# TELEGRAM ALERT FIX

if telegram_alert and green_trigger and not st.session_state.telegram_sent:

current_time=datetime.now().strftime("%I:%M:%S %p")

message=f"""
🟢 GREEN FLASH ALERT

Stock: {trigger_stock}
Price: ₹{trigger_price:.2f}
P2L: {trigger_p2l:.2f}%

Time: {current_time}
"""

url=f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

res=requests.post(url,data={
"chat_id":CHAT_ID,
"text":message
})

if res.status_code==200:

st.session_state.telegram_sent=True

if not green_trigger:

st.session_state.telegram_sent=False

# ---------------------------------------------------
# SOUND ALERT FIX

if sound_alert and green_trigger and not st.session_state.sound_sent:

st.session_state.sound_sent=True

if uploaded_sound:

st.audio(uploaded_sound, autoplay=True)

else:

st.audio(DEFAULT_SOUND_URL, autoplay=True)

if not green_trigger:

st.session_state.sound_sent=False

# ---------------------------------------------------
# HTML TABLE (SAME)

def generate_html_table(dataframe):

html="<table style='width:100%; border-collapse: collapse;'>"

html+="<tr>"

for col in dataframe.columns:

html+=f"<th style='padding:8px; border:1px solid #444;'>{col}</th>"

html+="</tr>"

for _,row in dataframe.iterrows():

html+="<tr>"

for col in dataframe.columns:

value=row[col]

style="padding:6px; border:1px solid #444; text-align:center;"

if col=="Stock":

if row["Stock"] in stockstar_list and row["P2L %"]<-5:

style+="color:green;font-weight:bold;animation: flash 1s infinite;"

elif row["Stock"] in stockstar_list and row["P2L %"]<-3:

style+="color:orange;font-weight:bold;"

elif row["P2L %"]<-2:

style+="color:hotpink;font-weight:bold;"

if col in ["P2L %","% Chg"]:

if value>0:
style+="color:green;font-weight:bold;"

elif value<0:
style+="color:red;font-weight:bold;"

if isinstance(value,float):

value=f"{value:.2f}"

html+=f"<td style='{style}'>{value}</td>"

html+="</tr>"

html+="</table>"

return html

st.markdown(generate_html_table(df), unsafe_allow_html=True)

# ---------------------------------------------------
# AVERAGE

average_p2l=df["P2L %"].mean()

st.markdown(f"### 📊 Average P2L of All Stocks is **{average_p2l:.2f}%**")
