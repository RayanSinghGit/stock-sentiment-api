import yfinance as yf
import requests
from flask import Blueprint, request, jsonify

ticker_bp = Blueprint("ticker_lookup", __name__)

# Function to fetch ticker based on user query
def search_ticker(query):
    url = f"https://query1.finance.yahoo.com/v1/finance/search?q={query}&lang=en-US"
    response = requests.get(url)

    if response.status_code == 200:
        results = response.json().get("quotes", [])
        return [
            {"symbol": res["symbol"], "name": res["shortname"]}
            for res in results if "symbol" in res
        ][:5]  # Limit to 5 results

    return []

# API route for ticker search
@ticker_bp.route("/search_ticker", methods=["GET"])
def get_ticker():
    query = request.args.get("query", "")
    if not query:
        return jsonify({"error": "No query provided"}), 400

    tickers = search_ticker(query)
    return jsonify({"tickers": tickers})

