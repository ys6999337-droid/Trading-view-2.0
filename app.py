import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf

st.title("🚀 AI Trading App (Stable No Error Version)")

symbol = st.text_input("Symbol", "BTC-USD")
interval = st.selectbox("Timeframe", ["1h","1d"])  # safe only

# DATA LOAD
try:
    df = yf.download(symbol, period="60d", interval=interval)
except:
    st.error("❌ Data load error")
    st.stop()

# CHECK
if df.empty:
    st.error("❌ Data nahi mila — symbol ya timeframe change karo")
    st.stop()

# INDICATORS
df["EMA"] = df["Close"].ewm(span=20).mean()

delta = df["Close"].diff()
gain = delta.clip(lower=0)
loss = -delta.clip(upper=0)
rs = gain.rolling(14).mean() / loss.rolling(14).mean()
df["RSI"] = 100 - (100/(1+rs))

df = df.dropna()

if len(df) < 30:
    st.error("❌ Data insufficient")
    st.stop()

# SIGNAL LOGIC (NO ML → NO ERROR)
last = df.iloc[-1]

if last["Close"] > last["EMA"] and last["RSI"] < 40:
    signal = "🔥 BUY"
elif last["Close"] < last["EMA"] and last["RSI"] > 60:
    signal = "🔻 SELL"
else:
    signal = "⚠️ WAIT"

# DISPLAY
st.subheader("📊 AI SIGNAL")

st.write(f"Signal: {signal}")
st.write(f"Price: {round(last['Close'],2)}")
st.write(f"RSI: {round(last['RSI'],2)}")

# CHART
st.subheader("📈 Chart")
st.line_chart(df["Close"])
