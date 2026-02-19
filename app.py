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

BOT_TOKEN = "YOUR_TOKEN"
CHAT_ID = "YOUR_CHAT_ID"

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
    "RELIANCE.NS": 1402.25,
    "HDFCBANK.NS": 896.50,
    "INFY.NS": 1278.30,
    "TCS.NS": 2578.54,
    "HINDALCO.NS": 878.80,
    "BSE.NS": 2718.29,
    "PIIND.NS": 2999.93,
    "MUTHOOTFIN.NS": 3431.50,
}

# ---------------------------------------------------
# FETCH DATA

@st.cache_data(ttl=60)
def fetch_data():

    symbols = list(stocks.keys())

    data = yf.download(
        tickers=symbols,
        period="1d",
        interval="1m",
        group_by="ticker",
        progress=False,
        threads=True
    )

    rows = []

    now = datetime.now()

    for sym in symbols:

        try:

            df_sym = data[sym]

            ref_low = stocks[sym]

            price = df_sym["Close"].iloc[-1]

            prev_close = df_sym["Close"].iloc[0]

            open_p = df_sym["Open"].iloc[-1]

            high = df_sym["High"].iloc[-1]

            low = df_sym["Low"].iloc[-1]

            # ---------------------------------------------------
            # DOWN MINUTES CALCULATION

            low_rows = df_sym[df_sym["Low"] <= ref_low]

            if not low_rows.empty:

                last_low_time = low_rows.index[-1].to_pydatetime()

                minutes_down = int(
                    (now - last_low_time).total_seconds() / 60
                )

            else:

                minutes_down = 999

            if minutes_down < 15:

                down_display = f"🟠 {minutes_down}"

            else:

                down_display = f"{minutes_down}"

            # ---------------------------------------------------

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

                "Low": low,

                "Down Minutes": down_display

            })

        except:

            pass

    return pd.DataFrame(rows)

# ---------------------------------------------------
# REFRESH BUTTON

if st.button("🔄 Refresh"):

    st.cache_data.clear()

    st.rerun()

# ---------------------------------------------------
# LOAD DATA

df = fetch_data()

# ---------------------------------------------------
# TELEGRAM ALERT

green_trigger = False

for _, row in df.iterrows():

    if row["Stock"] in stockstar_list and row["P2L %"] < -5:

        green_trigger = True

        trigger_stock = row["Stock"]

        trigger_price = row["Price"]

        trigger_p2l = row["P2L %"]

        break

if "alert_played" not in st.session_state:

    st.session_state.alert_played = False

if telegram_alert and green_trigger and not st.session_state.alert_played:

    current_time = datetime.now().strftime("%H:%M:%S")

    message = f"""

GREEN ALERT

Stock: {trigger_stock}

Price: {trigger_price:.2f}

P2L: {trigger_p2l:.2f}%

Time: {current_time}

"""

    requests.post(

        f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",

        data={

            "chat_id": CHAT_ID,

            "text": message

        }

    )

    st.session_state.alert_played = True

# ---------------------------------------------------
# TABLE

st.dataframe(df, use_container_width=True)

# ---------------------------------------------------
# SOUND ALERT

if sound_alert and green_trigger and not st.session_state.alert_played:

    st.session_state.alert_played = True

    if uploaded_sound:

        audio_bytes = uploaded_sound.read()

        b64 = base64.b64encode(audio_bytes).decode()

        st.markdown(

            f"""

            <audio autoplay>

            <source src="data:audio/mp3;base64,{b64}">

            </audio>

            """,

            unsafe_allow_html=True,

        )

    else:

        st.audio(DEFAULT_SOUND_URL, autoplay=True)

# ---------------------------------------------------
# AVERAGE

avg = df["P2L %"].mean()

st.write(f"Average P2L: {avg:.2f}%")
