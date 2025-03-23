from flask import Blueprint, request, jsonify
from api.stock_utils import get_stock_data
from api.news_fetcher import get_latest_news

stock_bp = Blueprint("stock", __name__)

@stock_bp.route("/api/get_stock", methods=["GET"])
def get_stock():
    ticker = request.args.get("ticker", "").upper()
    if not ticker:
        return jsonify({"error": "No ticker provided"}), 400

    stock_data = get_stock_data(ticker)
    if not stock_data:
        return jsonify({"error": "Invalid ticker or data unavailable"}), 400

    news_data = get_latest_news(ticker)
    stock_data["news"] = news_data["news"]
    stock_data["sentiment_score"] = news_data["sentiment_score"]

    return jsonify(stock_data)

