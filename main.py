import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
from sklearn.ensemble import RandomForestClassifier

st.set_page_config(layout="wide")
st.title("🚀 ALL-IN-ONE AI TRADING APP")

# ================= INPUT =================
symbol = st.text_input("Symbol", "BTC-USD")
interval = st.selectbox("Timeframe", ["5m","15m","1h"])

# ================= LOAD DATA =================
df = yf.download(symbol, period="30d", interval=interval)

# ================= FEATURES =================
df["EMA"] = df["Close"].ewm(span=20).mean()

delta = df["Close"].diff()
gain = delta.clip(lower=0)
loss = -delta.clip(upper=0)
rs = gain.rolling(14).mean() / loss.rolling(14).mean()
df["RSI"] = 100 - (100/(1+rs))

df["Return"] = df["Close"].pct_change()

# ================= TARGET =================
df["Target"] = (df["Close"].shift(-1) > df["Close"]).astype(int)

df = df.dropna()

# ================= MODEL TRAIN =================
X = df[["EMA","RSI","Return"]]
y = df["Target"]

model = RandomForestClassifier(n_estimators=100)
model.fit(X, y)

# ================= PREDICTION =================
last = df.iloc[-1]
X_last = [[last["EMA"], last["RSI"], last["Return"]]]

pred = model.predict(X_last)[0]
signal = "🔥 BUY" if pred == 1 else "🔻 SELL"

# ================= SL TP =================
atr = df["Close"].rolling(14).std().iloc[-1]

sl = last["Close"] - 1.5 * atr
tp = last["Close"] + 3 * atr

# ================= DISPLAY =================
col1, col2, col3 = st.columns(3)

col1.metric("Price", round(last["Close"],2))
col2.metric("AI Signal", signal)
col3.metric("RSI", round(last["RSI"],2))

st.write(f"Stop Loss: {round(sl,2)}")
st.write(f"Target: {round(tp,2)}")

# ================= CHART =================
st.subheader("📊 Price Chart")
st.line_chart(df["Close"])

# ================= BACKTEST =================
st.subheader("📈 Backtest")

balance = 10000
wins = 0
losses = 0

for i in range(1, len(df)-1):
    if df["Target"][i] == 1:
        entry = df["Close"][i]
        exit_price = df["Close"][i+1]

        if exit_price > entry:
            wins += 1
            balance += 100
        else:
            losses += 1
            balance -= 100

total = wins + losses
winrate = (wins/total)*100 if total > 0 else 0

st.write(f"Balance: ${balance}")
st.write(f"Winrate: {round(winrate,2)}%")
st.write(f"Trades: {total}")
