import yfinance as yf
import math
from api.stock_lookup import search_stock_ticker

# Ensure numbers are valid and prevent NaN issues
def safe_number(value, default=0):
    return value if isinstance(value, (int, float)) and not math.isnan(value) else default

# Calculate RSI (Relative Strength Index)
def calculate_rsi(hist, period=14):
    delta = hist['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()

    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

# Fetch stock data (Supports company name or ticker)
def get_stock_data(query):
    # Try to detect whether user provided a ticker or a company name
    if len(query) > 5 or " " in query:  
        ticker = search_stock_ticker(query)  # Convert name to ticker
        if not ticker:
            return {"error": "Company not found!"}
    else:
        ticker = query.upper()  # Assume valid ticker provided

    stock = yf.Ticker(ticker)
    hist = stock.history(period="6mo")

    if hist.empty:
        return None

    stock_info = stock.info

    sma_50 = safe_number(hist['Close'].rolling(window=50).mean().dropna().iloc[-1] if len(hist) >= 50 else None)
    sma_100 = safe_number(hist['Close'].rolling(window=100).mean().dropna().iloc[-1] if len(hist) >= 100 else None)
    sma_200 = safe_number(hist['Close'].rolling(window=200).mean().dropna().iloc[-1] if len(hist) >= 200 else None)

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
        "croci": stock_info.get("returnOnEquity"),
        "rsi_14": round(safe_number(calculate_rsi(hist).iloc[-1]), 2),
        "price_trend": list(hist['Close'].tail(5)),
    }

