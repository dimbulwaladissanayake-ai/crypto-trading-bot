import ccxt
import time
import os
import requests
import feedparser
import pandas as pd
from openai import OpenAI

# ==========================================
# 1. API CONFIGURATION (Environment Variables)
# ==========================================
BINANCE_API_KEY = os.environ.get('BINANCE_API_KEY')
BINANCE_SECRET = os.environ.get('BINANCE_SECRET')
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')

# OpenAI Client Setup
client = OpenAI(api_key=OPENAI_API_KEY)

# ==========================================
# 2. EXCHANGE SETUP (Binance Testnet Demo)
# ==========================================
exchange = ccxt.binance({
    'apiKey': BINANCE_API_KEY,
    'secret': BINANCE_SECRET,
    'enableRateLimit': True,
    'options': {'defaultType': 'future'}
})

# Binance Testnet / Demo Trading URLs
exchange.urls['api'] = {
    'public': 'https://testnet.binancevision.com/api/v1',
    'private': 'https://testnet.binancevision.com/api/v1',
    'fapiPublic': 'https://testnet.binancefuture.com/fapi/v1',
    'fapiPrivate': 'https://testnet.binancefuture.com/fapi/v1',
}

SYMBOL = 'BTC/USDT:USDT'
MAX_LOSS_USD = 0.50
CURRENT_POSITION = None

print("========================================")
print("🚀 BINANCE TESTNET AI TRADING BOT ACTIVE")
print("========================================")

def get_market_news_sentiment():
    try:
        rss_url = "https://news.google.com/rss/search?q=Bitcoin+Crypto&hl=en-US&gl=US&ceid=US:en"
        feed = feedparser.parse(rss_url)
        headlines = [entry.title for entry in feed.entries[:5]]
        
        if not headlines:
            return "NEUTRAL"

        news_text = " | ".join(headlines)
        prompt = f"Analyze the following crypto news headlines and return ONLY ONE word: 'BULLISH', 'BEARISH', or 'NEUTRAL'. Headlines: {news_text}"
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=10
        )
        sentiment = response.choices[0].message.content.strip().upper()
        return sentiment if sentiment in ['BULLISH', 'BEARISH', 'NEUTRAL'] else 'NEUTRAL'
    except Exception as e:
        print(f"News Fetch Error: {e}")
        return "NEUTRAL"

def calculate_atr(symbol, limit=14):
    try:
        ohlcv = exchange.fetch_ohlcv(symbol, timeframe='1h', limit=limit+1)
        df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        df['tr'] = pd.maximum(
            df['high'] - df['low'],
            pd.maximum(
                abs(df['high'] - df['close'].shift(1)),
                abs(df['low'] - df['close'].shift(1))
            )
        )
        atr = df['tr'].rolling(window=limit).mean().iloc[-1]
        return atr
    except Exception as e:
        print(f"ATR Calculation Error: {e}")
        return 50.0

while True:
    try:
        print("\n----------------------------------------")
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Checking market conditions...")
        
        ticker = exchange.fetch_ticker(SYMBOL)
        current_price = ticker['last']
        atr = calculate_atr(SYMBOL)
        print(f"Current Price: {current_price} | ATR: {atr:.2f}")

        sentiment = get_market_news_sentiment()
        print(f"AI News Sentiment: {sentiment}")

        if sentiment == 'BULLISH' and CURRENT_POSITION != 'BUY':
            print("🟢 Bullish signal detected! Executing BUY (Long)...")
            CURRENT_POSITION = 'BUY'
            
        elif sentiment == 'BEARISH' and CURRENT_POSITION != 'SELL':
            print("🔴 Bearish signal detected! Executing SELL (Short) & Flipping...")
            CURRENT_POSITION = 'SELL'
            
        else:
            print(f"Holding current position state: {CURRENT_POSITION}")

        time.sleep(60)

    except Exception as e:
        print(f"❌ Main Loop Error: {e}")
        time.sleep(10)