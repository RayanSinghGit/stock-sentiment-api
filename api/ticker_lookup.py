from flask import Blueprint, request, jsonify
import yfinance as yf
import requests

ticker_lookup_bp = Blueprint("ticker_lookup", __name__)

# Helper Function: Search Stocks Manually
def search_stocks(query):
    search_url = f"https://query2.finance.yahoo.com/v1/finance/search?q={query}&quotesCount=5"
    headers = {"User-Agent": "Mozilla/5.0"}
    
    try:
        response = requests.get(search_url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            results = [
                {"ticker": item["symbol"], "name": item["shortname"], "exchange": item["exchange"]}
                for item in data.get("quotes", [])
            ]
            return results
    except Exception as e:
        print(f"Error searching for stocks: {e}")
    
    return []

# API Route: Search Stocks by Name
@ticker_lookup_bp.route("/api/search_ticker", methods=["GET"])
def search_ticker():
    query = request.args.get("query", "").strip()
    if not query:
        return jsonify([])  # Return empty list if no query

    results = search_stocks(query)
    return jsonify(results)

