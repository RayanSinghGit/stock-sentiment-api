from flask import Blueprint, request, jsonify
import yfinance as yf

ticker_bp = Blueprint("ticker", __name__)

def search_stocks(query):
    query = query.lower()
    stocks = yf.Ticker(query)
    try:
        info = stocks.info
        name = info.get("longName", query)
        symbol = info.get("symbol", query.upper())
        return [{"name": name, "symbol": symbol}]
    except Exception:
        return []

@ticker_bp.route("/api/search_ticker", methods=["GET"])
def search_ticker():
    query = request.args.get("query", "")
    if not query:
        return jsonify([])
    results = search_stocks(query)
    return jsonify(results)

