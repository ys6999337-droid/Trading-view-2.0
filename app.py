import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import json, os
from datetime import datetime

st.set_page_config(layout="wide")
st.title("🚀 AI TRADING PLATFORM")

# ================= FILES =================
USERS = "users.json"
TRADES = "trades.csv"

if not os.path.exists(USERS):
    json.dump({}, open(USERS,"w"))

if not os.path.exists(TRADES):
    pd.DataFrame(columns=["user","time","symbol","side","price","profit"]).to_csv(TRADES,index=False)

users = json.load(open(USERS))

# ================= SESSION =================
if "user" not in st.session_state:
    st.session_state.user = None

# ================= LOGIN UI =================
if st.session_state.user is None:

    mode = st.radio("Select Option", ["Login", "Signup"])

    # SIGNUP
    if mode == "Signup":
        st.subheader("Create Account")

        u = st.text_input("Username")
        p = st.text_input("Password", type="password")

        if st.button("Signup"):
            if u in users:
                st.error("User exists")
            elif u == "" or p == "":
                st.error("Enter details")
            else:
                users[u] = p
                json.dump(users, open(USERS,"w"))
                st.success("Account created ✅")

    # LOGIN
    else:
        st.subheader("Login")

        u = st.text_input("Username")
        p = st.text_input("Password", type="password")

        if st.button("Login"):
            if u in users and users[u] == p:
                st.session_state.user = u
                st.success("Login successful 🎉")
                st.rerun()
            else:
                st.error("Invalid login ❌")

# ================= MAIN APP =================
else:

    st.success(f"👤 Logged in as {st.session_state.user}")

    if st.button("Logout"):
        st.session_state.user = None
        st.rerun()

    symbol = st.text_input("Symbol", "BTC-USD")
    interval = st.selectbox("Timeframe", ["1h","1d"])

    # DATA
    @st.cache_data(ttl=300)
    def load(sym):
        df = yf.download(sym, period="60d", interval=interval, progress=False)
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        return df

    df = load(symbol)

    if df.empty:
        st.error("Data error")
        st.stop()

    df["Close"] = pd.to_numeric(df["Close"], errors="coerce")

    # INDICATORS
    df["EMA"] = df["Close"].ewm(20).mean()

    delta = df["Close"].diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    rs = gain.rolling(14).mean()/loss.rolling(14).mean()
    df["RSI"] = 100-(100/(1+rs))

    df = df.dropna()

    last = df.iloc[-1]
    close = float(last["Close"])
    ema = float(last["EMA"])
    rsi = float(last["RSI"])

    # SIGNAL
    if close > ema and rsi < 40:
        signal = "BUY"
    elif close < ema and rsi > 60:
        signal = "SELL"
    else:
        signal = "WAIT"

    c1,c2,c3 = st.columns(3)
    c1.metric("Price", round(close,2))
    c2.metric("Signal", signal)
    c3.metric("RSI", round(rsi,2))

    # TRADE
    st.subheader("💰 Trade")

    if st.button("Execute Trade"):
        profit = np.random.uniform(-2,5)

        new = pd.DataFrame([{
            "user": st.session_state.user,
            "time": datetime.now(),
            "symbol": symbol,
            "side": signal,
            "price": close,
            "profit": profit
        }])

        old = pd.read_csv(TRADES)
        pd.concat([old,new]).to_csv(TRADES,index=False)

        st.success("Trade Done")

    
import streamlit as st

st.title("📊 Pro Chart Analysis")

symbol = st.text_input("Symbol", "BINANCE:BTCUSDT")

# TradingView Widget
html_code = f"""
<!-- TradingView Widget BEGIN -->
<div class="tradingview-widget-container">
  <div id="tradingview_chart"></div>
  <script src="https://s3.tradingview.com/tv.js"></script>
  <script>
  new TradingView.widget({{
    "width": "100%",
    "height": 600,
    "symbol": "{symbol}",
    "interval": "60",
    "timezone": "Asia/Kolkata",
    "theme": "dark",
    "style": "1",
    "locale": "en",
    "toolbar_bg": "#f1f3f6",
    "enable_publishing": false,
    "allow_symbol_change": true,
    "studies": ["RSI@tv-basicstudies","MACD@tv-basicstudies"],
    "container_id": "tradingview_chart"
  }});
  </script>
</div>
"""

st.components.v1.html(html_code, height=650)

    # HISTORY
    st.subheader("📜 My Trades")

    trades = pd.read_csv(TRADES)
    my = trades[trades["user"] == st.session_state.user]

    st.dataframe(my)

    # PERFORMANCE
    st.subheader("📈 Performance")

    if not my.empty:
        total = my["profit"].sum()
        wins = len(my[my["profit"] > 0])
        loss = len(my[my["profit"] <= 0])

        k1,k2,k3 = st.columns(3)
        k1.metric("Profit", round(total,2))
        k2.metric("Wins", wins)
        k3.metric("Loss", loss)

        st.line_chart(my["profit"].cumsum())
