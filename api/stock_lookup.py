import yfinance as yf
import requests

# API Key for FMP (Financial Modeling Prep) - REQUIRED for US stock search
FMP_API_KEY = "YOUR_FMP_API_KEY"  # Replace with your actual API key

# Function to search stock ticker by name
def search_stock_ticker(company_name, market="auto"):
    """
    Search for a stock ticker based on a company name.
    - market="auto" detects if it's a US or Indian stock.
    - market="NSE" or "BSE" forces Indian stock lookup.
    - market="US" forces US stock lookup.
    """

    # 1️⃣ If Indian market, use NSE/BSE lookup
    if market in ["NSE", "BSE"]:
        nse_ticker = company_name.replace(" ", "").upper() + ".NS"
        bse_ticker = company_name.replace(" ", "").upper() + ".BO"

        # Validate if the ticker exists in Yahoo Finance
        if yf.Ticker(nse_ticker).history(period="1d").empty:
            if yf.Ticker(bse_ticker).history(period="1d").empty:
                return None  # No valid ticker found
            return bse_ticker  # Return valid BSE ticker
        return nse_ticker  # Return valid NSE ticker

    # 2️⃣ If US market or unknown, use FMP API
    url = f"https://financialmodelingprep.com/api/v3/search?query={company_name}&limit=1&apikey={FMP_API_KEY}"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        if data:
            return data[0]["symbol"]  # Return first match

    return None  # No match found

