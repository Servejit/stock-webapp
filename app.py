!pip install yfinance ipywidgets pandas --quiet

import yfinance as yf
import pandas as pd
import ipywidgets as widgets
from IPython.display import display, clear_output

# -----------------------------------
# UPDATED STOCK LIST (Stock : Reference Low Price)
stocks = {
    "AMBUJACEM.NS": 492.12,
    "BAJAJFINSV.NS": 1867.22,
    "BAJAJHLDNG.NS": 10348.00,
    "BANKBARODA.NS": 269.82,
    "BEL.NS": 423.42,
    "BOSCHLTD.NS": 35596.13,
    "COALINDIA.NS": 411.97,
    "DRREDDY.NS": 1161.26,
    "FEDERALBNK.NS": 274.62,
    "FORTIS.NS": 808.54,
    "GAIL.NS": 157.01,
    "GRASIM.NS": 2699.44,
    "HDFCLIFE.NS": 695.06,
    "HINDALCO.NS": 917.39,
    "INDUSINDBK.NS": 890.53,
    "IRCTC.NS": 593.02,
    "IRFC.NS": 110.97,
    "ITC.NS": 300.49,
    "JINDALSTEL.NS": 1077.29,
    "JIOFIN.NS": 236.41,
    "LICI.NS": 784.51,
    "MARICO.NS": 704.76,
    "MARUTI.NS": 13987.71,
    "MUTHOOTFIN.NS": 3401.97,
    "NAUKRI.NS": 1113.01,
    "NHPC.NS": 74.56,
    "NMDC.NS": 78.03,
    "OBEROIRLTY.NS": 1421.86,
    "OFSS.NS": 7109.28,
    "ONGC.NS": 246.98,
    "PIIND.NS": 2995.95,
    "PNB.NS": 117.56,
    "POLICYBZR.NS": 1445.38,
    "POWERGRID.NS": 248.75,
    "SBICARD.NS": 723.34,
    "SHREECEM.NS": 25979.45,
    "SOLARINDS.NS": 12796.70,
    "SUZLON.NS": 45.18,
    "TATAPOWER.NS": 346.66,
    "TATASTEEL.NS": 182.09,
    "TCS.NS": 2901.42,
    "TORNTPHARM.NS": 3889.26,
    "TRENT.NS": 3626.78,
    "ULTRACEMCO.NS": 12130.05,
    "VBL.NS": 430.04
}

# -----------------------------------
# FUNCTION TO FETCH DATA
def fetch_data():
    rows = []
    for sym, ref_low in stocks.items():
        try:
            t = yf.Ticker(sym)
            info = t.info

            price = info.get("regularMarketPrice", 0)
            p2l = ((price - ref_low) / ref_low) * 100

            rows.append({
                "Stock": info.get("shortName", sym.replace(".NS","")),
                "P2L %": p2l,
                "Price": price,
                "% Chg": info.get("regularMarketChangePercent", 0),
                "Low Price": ref_low,
                "Open": info.get("open", 0),
                "High": info.get("dayHigh", 0),
                "Low": info.get("dayLow", 0)
            })
        except:
            pass

    return pd.DataFrame(rows)

# -----------------------------------
# STYLING

df_global = pd.DataFrame()

def color_text(col):
    pink_cols = ["Open", "High", "Low"]

    # Stock column: pink only if P2L negative
    if col.name == "Stock":
        return [
            "color: hotpink" if p2l < 0 else "color: black"
            for p2l in df_global["P2L %"]
        ]

    # Open High Low always pink
    if col.name in pink_cols:
        return ["color: hotpink"] * len(col)

    # Everything else normal
    return ["color: black"] * len(col)

def style_df(df):
    num_cols = df.select_dtypes(include="number").columns
    return (
        df.style
        .apply(color_text)
        .format("{:.2f}", subset=num_cols)
        .set_properties(**{"font-size": "11px"})
    )

# -----------------------------------

output = widgets.Output()

def show(df, title):
    global df_global
    df_global = df.copy()

    with output:
        clear_output()
        print(title)
        display(style_df(df))

def refresh(b=None):
    show(fetch_data(), "📊 Live Prices with P2L")

def sort_p2l(b=None):
    df = fetch_data().sort_values("P2L %", ascending=False)
    show(df, "📊 Sorted by P2L %")

# -----------------------------------
# BUTTONS

btn_r1 = widgets.Button(description="🔄 Refresh", button_style="info")
btn_s1 = widgets.Button(description="📈 Sort P2L", button_style="success")

btn_r2 = widgets.Button(description="🔄 Refresh", button_style="info")
btn_s2 = widgets.Button(description="📈 Sort P2L", button_style="success")

btn_r1.on_click(refresh)
btn_r2.on_click(refresh)
btn_s1.on_click(sort_p2l)
btn_s2.on_click(sort_p2l)

display(widgets.HBox([btn_r1, btn_s1]))
display(output)
display(widgets.HBox([btn_r2, btn_s2]))

# -----------------------------------
# AUTO LOAD
refresh()
