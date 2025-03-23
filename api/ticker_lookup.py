import yfinance as yf

def search_stocks(query):
    query = query.lower()

    # Get all S&P 500 and major tickers from yfinance
    tickers = yf.Tickers(" ".join(["AAPL", "MSFT", "GOOGL", "AMZN", "META", "TSLA", "TCS.NS", "TATAMOTORS.NS", "TATASTEEL.NS", "TATAPOWER.NS", "INFY.NS", "RELIANCE.NS", "HDFCBANK.NS"]))

    matches = []

    for symbol, stock in tickers.tickers.items():
        try:
            info = stock.info
            name = info.get("shortName", "").lower()
            full_name = info.get("longName", "").lower()
            sym = symbol.lower()

            # Match if query is in symbol, shortName, or longName
            if query in sym or query in name or query in full_name:
                matches.append({
                    "symbol": symbol.upper(),
                    "name": info.get("longName") or info.get("shortName") or symbol.upper()
                })

        except Exception:
            continue  # Skip any failed ticker fetches

    return matches

