import requests

# Convert a user-friendly name into the correct ticker format
def get_full_ticker(query):
    query = query.upper().strip()
    
    # Map user input to proper tickers
    manual_mapping = {
        "TATA MOTORS": "TATAMOTORS.NS",
        "RELIANCE": "RELIANCE.NS",
        "HDFC BANK": "HDFCBANK.NS",
    }
    
    if query in manual_mapping:
        return manual_mapping[query]

    # Default to NSE ticker (yfinance format)
    return f"{query}.NS"

