import yfinance as yf

# Helper: Ensure correct ticker format (handles NSE/BSE)
def get_full_ticker(ticker):
    try:
        stock = yf.Ticker(ticker)
        stock_info = stock.info
        exchange = stock_info.get("exchange", "").upper()

        if exchange == "NSE":
            return f"{ticker}.NS"
        elif exchange == "BSE":
            return f"{ticker}.BO"
        else:
            return ticker  # US stocks remain unchanged
    except:
        return ticker

# Fetch stock data
def get_stock_data(ticker):
    ticker = get_full_ticker(ticker)  # Fix ticker
    stock = yf.Ticker(ticker)
    hist = stock.history(period="6mo")

    if hist.empty:
        return None

    stock_info = stock.info

    return {
        "stock_name": stock_info.get("longName", ticker),
        "current_price": stock_info.get("currentPrice"),
        "previous_close": stock_info.get("previousClose"),
        "market_cap": stock_info.get("marketCap"),
        "price_trend": list(hist['Close'].tail(5)),
    }

