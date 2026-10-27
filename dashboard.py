import streamlit as st
import ccxt
import os
import pandas as pd
import time

# Page Configuration
st.set_page_config(
    page_title="AI Crypto Trading Dashboard",
    page_icon="📈",
    layout="wide"
)

# Binance Setup (Environment Variables)
BINANCE_API_KEY = os.environ.get('BINANCE_API_KEY')
BINANCE_SECRET = os.environ.get('BINANCE_SECRET')

exchange = ccxt.binance({
    'apiKey': BINANCE_API_KEY,
    'secret': BINANCE_SECRET,
    'enableRateLimit': True,
    'options': {'defaultType': 'future'}
})

exchange.urls['api'] = {
    'public': 'https://testnet.binancevision.com/api/v1',
    'private': 'https://testnet.binancevision.com/api/v1',
    'fapiPublic': 'https://testnet.binancefuture.com/fapi/v1',
    'fapiPrivate': 'https://testnet.binancefuture.com/fapi/v1',
}

# Header
st.title("🚀 Binance Testnet AI Trading Dashboard")
st.write("Live Real-Time Trading Performance & Analytics")

# Auto refresh option
st.sidebar.header("Dashboard Settings")
auto_refresh = st.sidebar.checkbox("Auto Refresh (Every 10s)", value=True)

try:
    balance = exchange.fetch_balance()
    usdt_balance = balance['total'].get('USDT', 0.0)
    free_usdt = balance['free'].get('USDT', 0.0)

    # Top Metrics Bar
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(label="Total Balance (USDT)", value=f"${usdt_balance:.2f}")
    with col2:
        st.metric(label="Available Balance", value=f"${free_usdt:.2f}")
    with col3:
        st.metric(label="Bot Status", value="ACTIVE 🟢")
    with col4:
        st.metric(label="Max Loss Cut", value="$0.50 Limit")

    st.markdown("---")

    # Live Price Chart
    st.subheader("📊 Live Market Price (BTC/USDT)")
    ticker = exchange.fetch_ticker('BTC/USDT:USDT')
    st.write(f"**Current Price:** ${ticker['last']:,.2f}")

    # Fetch Open Positions
    st.subheader("⚡ Open Positions (Active Trades)")
    positions = exchange.fetch_positions(['BTC/USDT:USDT'])
    active_positions = [p for p in positions if float(p['contracts']) > 0]

    if active_positions:
        pos_data = []
        for pos in active_positions:
            pos_data.append({
                "Symbol": pos['symbol'],
                "Side": pos['side'].upper(),
                "Contracts": pos['contracts'],
                "Entry Price": pos['entryPrice'],
                "Unrealized PnL ($)": pos['unrealizedPnl']
            })
        st.table(pd.DataFrame(pos_data))
    else:
        st.info("No active open trades at the moment.")

except Exception as e:
    st.error(f"Error connecting to Binance: {e}")

# Auto Refresh Control
if auto_refresh:
    time.sleep(10)
    st.rerun()