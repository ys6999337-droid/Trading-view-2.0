import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import time

st.title("🚀 AI Trading App (No Rate Limit Fix)")

symbol = st.text_input("Symbol", "BTC-USD")
interval = st.selectbox("Timeframe", ["1h","1d"])

# ✅ CACHE (IMPORTANT FIX)
@st.cache_data(ttl=300)  # 5 min cache
def load_data(symbol, interval):
    try:
        df = yf.download(symbol, period="60d", interval=interval, progress=False)
        return df
    except:
        return pd.DataFrame()

# LOAD DATA
df = load_data(symbol, interval)

# CHECK
if df is None or df.empty:
    st.error("❌ Data blocked by Yahoo (refresh after 1-2 min)")
    st.stop()

# CALCULATIONS
df["EMA"] = df["Close"].ewm(span=20).mean()

delta = df["Close"].diff()
gain = delta.clip(lower=0)
loss = -delta.clip(upper=0)
rs = gain.rolling(14).mean() / loss.rolling(14).mean()
df["RSI"] = 100 - (100/(1+rs))

df = df.dropna()

if len(df) < 20:
    st.error("❌ Not enough data")
    st.stop()

last = df.iloc[-1]

# SIGNAL
if last["Close"] > last["EMA"] and last["RSI"] < 40:
    signal = "🔥 BUY"
elif last["Close"] < last["EMA"] and last["RSI"] > 60:
    signal = "🔻 SELL"
else:
    signal = "⚠️ WAIT"

# DISPLAY
st.subheader("📊 SIGNAL")
st.write(f"Signal: {signal}")
st.write(f"Price: {round(last['Close'],2)}")

# CHART
st.line_chart(df["Close"])
