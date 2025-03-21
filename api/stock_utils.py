import yfinance as yf
import math
import pandas as pd
from .ticker_lookup import get_full_ticker

# Ensure numbers are valid and prevent NaN issues
def safe_number(value, default=0):
    return value if isinstance(value, (int, float)) and not math.isnan(value) else default

# Calculate RSI
def calculate_rsi(data, window=14):
    delta = data["Close"].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

# Fetch stock data (supports NSE & BSE)
def get_stock_data(ticker):
    ticker = get_full_ticker(ticker)  # Convert to full ticker if needed
    stock = yf.Ticker(ticker)
    hist = stock.history(period="6mo")

    if hist.empty:
        return None

    stock_info = stock.info

    sma_50 = safe_number(hist['Close'].rolling(window=50).mean().dropna().iloc[-1] if len(hist) >= 50 else None)
    sma_100 = safe_number(hist['Close'].rolling(window=100).mean().dropna().iloc[-1] if len(hist) >= 100 else None)
    sma_200 = safe_number(hist['Close'].rolling(window=200).mean().dropna().iloc[-1] if len(hist) >= 200 else None)
    rsi_14 = round(safe_number(calculate_rsi(hist).iloc[-1]), 2) if len(hist) >= 14 else None

    return {
        "stock_name": stock_info.get("longName", ticker),
        "current_price": stock_info.get("currentPrice"),
        "previous_close": stock_info.get("previousClose"),
        "market_cap": stock_info.get("marketCap"),
        "pe_ratio": stock_info.get("trailingPE"),
        "pb_ratio": stock_info.get("priceToBook"),
        "eps": stock_info.get("trailingEps"),
        "sma_50": round(sma_50, 2),
        "sma_100": round(sma_100, 2),
        "sma_200": round(sma_200, 2),
        "rsi_14": rsi_14,
        "price_trend": list(hist['Close'].tail(5)),
    }

