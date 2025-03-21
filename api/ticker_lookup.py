import yfinance as yf
from flask import Blueprint, request, jsonify

ticker_bp = Blueprint("ticker", __name__)

@ticker_bp.route("/search_ticker", methods=["GET"])
def search_ticker():
    query = request.args.get("query", "").strip().lower()
    
    if not query:
        return jsonify({"error": "Query is required"}), 400

    try:
        # Use Yahoo Finance API to search for stocks
        matches = yf.search(query)
        results = []

        for item in matches.get("quotes", []):
            results.append({
                "ticker": item["symbol"],
                "name": item["shortname"],
                "exchange": item["exchange"]
            })

        return jsonify(results)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

