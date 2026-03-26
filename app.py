import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf

st.title("🚀 AI Trading App (FINAL ULTRA FIX)")

symbol = st.text_input("Symbol", "BTC-USD")
interval = st.selectbox("Timeframe", ["1h","1d"])

@st.cache_data(ttl=300)
def load_data(symbol, interval):
    df = yf.download(symbol, period="60d", interval=interval, progress=False)
    
    # ✅ FLATTEN COLUMNS (MAIN FIX)
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    
    return df

df = load_data(symbol, interval)

if df is None or df.empty:
    st.error("❌ Data load failed")
    st.stop()

# SAFE CONVERT
df["Close"] = pd.to_numeric(df["Close"], errors='coerce')

# INDICATORS
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

# ✅ FORCE SCALAR (CRITICAL FIX)
close = float(last["Close"])
ema = float(last["EMA"])
rsi = float(last["RSI"])

# SIGNAL
if close > ema and rsi < 40:
    signal = "🔥 BUY"
elif close < ema and rsi > 60:
    signal = "🔻 SELL"
else:
    signal = "⚠️ WAIT"

# OUTPUT
st.subheader("📊 SIGNAL")
st.write(f"Signal: {signal}")
st.write(f"Price: {round(close,2)}")
st.write(f"RSI: {round(rsi,2)}")

# CHART
st.line_chart(df["Close"])
