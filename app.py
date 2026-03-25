import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
from sklearn.ensemble import RandomForestClassifier

st.title("🚀 AI Trading App (Fixed Version)")

symbol = st.text_input("Symbol", "BTC-USD")
interval = st.selectbox("Timeframe", ["5m","15m","1h"])

# SAFE DATA LOAD
try:
    df = yf.download(symbol, period="7d", interval=interval)
except:
    st.error("Data load error")
    st.stop()

# CHECK DATA
if df.empty:
    st.error("❌ No data मिला (change timeframe या symbol)")
    st.stop()

# FEATURES
df["EMA"] = df["Close"].ewm(span=20).mean()

delta = df["Close"].diff()
gain = delta.clip(lower=0)
loss = -delta.clip(upper=0)
rs = gain.rolling(14).mean() / loss.rolling(14).mean()
df["RSI"] = 100 - (100/(1+rs))

df["Return"] = df["Close"].pct_change()

# TARGET
df["Target"] = (df["Close"].shift(-1) > df["Close"]).astype(int)

df = df.dropna()

# AGAIN CHECK
if len(df) < 20:
    st.error("❌ Data kam hai (change timeframe)")
    st.stop()

# MODEL
X = df[["EMA","RSI","Return"]]
y = df["Target"]

model = RandomForestClassifier()
model.fit(X, y)

# PREDICTION
last = df.iloc[-1]
X_last = [[last["EMA"], last["RSI"], last["Return"]]]

pred = model.predict(X_last)[0]

signal = "🔥 BUY" if pred == 1 else "🔻 SELL"

# DISPLAY
st.write(f"Signal: {signal}")
st.write(f"Price: {round(last['Close'],2)}")

# CHART
st.line_chart(df["Close"])
