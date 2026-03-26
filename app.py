import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf

st.title("🚀 AI Trading App (FINAL FIXED)")

symbol = st.text_input("Symbol", "BTC-USD")
interval = st.selectbox("Timeframe", ["1h","1d"])

# LOAD DATA
df = yf.download(symbol, period="60d", interval=interval)

# CHECK DATA
if df is None or df.empty:
    st.error("❌ Data load failed")
    st.stop()

# CALCULATIONS
df["EMA"] = df["Close"].ewm(span=20).mean()

delta = df["Close"].diff()
gain = delta.clip(lower=0)
loss = -delta.clip(upper=0)
rs = gain.rolling(14).mean() / loss.rolling(14).mean()
df["RSI"] = 100 - (100/(1+rs))

# CLEAN DATA
df = df.dropna()

# FINAL SAFETY CHECK
if df.empty or len(df) < 10:
    st.error("❌ Not enough valid data")
    st.stop()

# SAFE LAST ROW
last = df.iloc[-1]

# EXTRA SAFETY (NO CRASH)
if pd.isna(last["Close"]) or pd.isna(last["EMA"]) or pd.isna(last["RSI"]):
    st.error("❌ Indicator error — reload app")
    st.stop()

# SIGNAL LOGIC
if last["Close"] > last["EMA"] and last["RSI"] < 40:
    signal = "🔥 BUY"
elif last["Close"] < last["EMA"] and last["RSI"] > 60:
    signal = "🔻 SELL"
else:
    signal = "⚠️ WAIT"

# OUTPUT
st.subheader("📊 SIGNAL")

st.write(f"Signal: {signal}")
st.write(f"Price: {round(last['Close'],2)}")
st.write(f"RSI: {round(last['RSI'],2)}")

# CHART
st.line_chart(df["Close"])
