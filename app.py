import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
from sklearn.ensemble import RandomForestClassifier

st.title("🚀 AI Trading App (Stable Version)")

symbol = st.text_input("Symbol", "BTC-USD")
interval = st.selectbox("Timeframe", ["15m","1h","1d"])  # 5m हटाया

# SAFE DOWNLOAD FUNCTION
def load_data():
    try:
        df = yf.download(symbol, period="30d", interval=interval)
        return df
    except:
        return pd.DataFrame()

df = load_data()

# CHECK DATA
if df is None or df.empty:
    st.error("❌ Data load nahi hua — timeframe change karo (1h try karo)")
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

# FINAL CHECK
if len(df) < 30:
    st.error("❌ Data insufficient — timeframe 1h ya 1d use karo")
    st.stop()

# MODEL TRAIN
X = df[["EMA","RSI","Return"]]
y = df["Target"]

model = RandomForestClassifier(n_estimators=50)
model.fit(X, y)

# PREDICTION
last = df.iloc[-1]
X_last = [[last["EMA"], last["RSI"], last["Return"]]]

pred = model.predict(X_last)[0]

signal = "🔥 BUY" if pred == 1 else "🔻 SELL"

# DISPLAY
st.subheader("📊 AI SIGNAL")

st.write(f"Signal: {signal}")
st.write(f"Price: {round(last['Close'],2)}")
st.write(f"RSI: {round(last['RSI'],2)}")

# CHART
st.subheader("📈 Chart")
st.line_chart(df["Close"])
