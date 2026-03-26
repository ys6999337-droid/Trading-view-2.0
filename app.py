import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import json
import os
from datetime import datetime

st.set_page_config(layout="wide")
st.title("🚀 AI TRADING SAAS PLATFORM")

# ================== DATABASE ==================
USERS_FILE = "users.json"
TRADES_FILE = "trades.csv"

# create files if not exist
if not os.path.exists(USERS_FILE):
    with open(USERS_FILE, "w") as f:
        json.dump({}, f)

if not os.path.exists(TRADES_FILE):
    pd.DataFrame(columns=["user","time","symbol","side","price","profit"]).to_csv(TRADES_FILE, index=False)

# ================== USER SYSTEM ==================
def load_users():
    return json.load(open(USERS_FILE))

def save_users(data):
    json.dump(data, open(USERS_FILE, "w"))

users = load_users()

menu = st.sidebar.selectbox("Menu", ["Login","Signup"])

if "user" not in st.session_state:
    st.session_state.user = None

if menu == "Signup":
    u = st.text_input("Username")
    p = st.text_input("Password", type="password")

    if st.button("Create Account"):
        if u in users:
            st.error("User exists")
        else:
            users[u] = p
            save_users(users)
            st.success("Account created")

elif menu == "Login":
    u = st.text_input("Username")
    p = st.text_input("Password", type="password")

    if st.button("Login"):
        if u in users and users[u] == p:
            st.session_state.user = u
            st.success("Logged in")
        else:
            st.error("Invalid login")

# ================== MAIN APP ==================
if st.session_state.user:

    st.sidebar.success(f"👤 {st.session_state.user}")

    symbol = st.text_input("Symbol", "BTC-USD")
    interval = st.selectbox("Timeframe", ["1h","1d"])

    # ================== DATA ==================
    @st.cache_data(ttl=300)
    def load_data(sym):
        df = yf.download(sym, period="60d", interval=interval, progress=False)
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        return df

    df = load_data(symbol)

    if df.empty:
        st.error("Data load failed")
        st.stop()

    df["Close"] = pd.to_numeric(df["Close"], errors="coerce")

    # ================== INDICATORS ==================
    df["EMA"] = df["Close"].ewm(span=20).mean()

    delta = df["Close"].diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    rs = gain.rolling(14).mean() / loss.rolling(14).mean()
    df["RSI"] = 100 - (100/(1+rs))

    df = df.dropna()

    last = df.iloc[-1]

    close = float(last["Close"])
    ema = float(last["EMA"])
    rsi = float(last["RSI"])

    # ================== SIGNAL ==================
    def get_signal(c,e,r):
        if c > e and r < 40:
            return "BUY"
        elif c < e and r > 60:
            return "SELL"
        return "WAIT"

    signal = get_signal(close, ema, rsi)

    col1, col2, col3 = st.columns(3)
    col1.metric("Price", round(close,2))
    col2.metric("Signal", signal)
    col3.metric("RSI", round(rsi,2))

    # ================== TRADE ==================
    st.subheader("💰 Execute Trade (Simulated SaaS)")

    if st.button("Run Trade"):
        profit = np.random.uniform(-2,5)  # demo profit

        new_trade = pd.DataFrame([{
            "user": st.session_state.user,
            "time": datetime.now(),
            "symbol": symbol,
            "side": signal,
            "price": close,
            "profit": profit
        }])

        df_old = pd.read_csv(TRADES_FILE)
        df_new = pd.concat([df_old, new_trade])
        df_new.to_csv(TRADES_FILE, index=False)

        st.success("Trade executed")

    # ================== CHART ==================
    st.subheader("📊 Chart")
    st.line_chart(df["Close"])

    # ================== HISTORY ==================
    st.subheader("📜 My Trades")

    trades = pd.read_csv(TRADES_FILE)
    my_trades = trades[trades["user"] == st.session_state.user]

    st.dataframe(my_trades)

    # ================== PERFORMANCE ==================
    st.subheader("📈 Performance")

    if not my_trades.empty:
        total = my_trades["profit"].sum()
        wins = len(my_trades[my_trades["profit"] > 0])
        loss = len(my_trades[my_trades["profit"] <= 0])

        c1, c2, c3 = st.columns(3)
        c1.metric("Profit", round(total,2))
        c2.metric("Wins", wins)
        c3.metric("Loss", loss)

        st.line_chart(my_trades["profit"].cumsum())
    else:
        st.write("No trades yet")

else:
    st.warning("Login first")
