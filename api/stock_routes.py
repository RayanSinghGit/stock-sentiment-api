from flask import Blueprint, jsonify, request
from .stock_utils import get_stock_data
from .news_fetcher import get_latest_news

api_bp = Blueprint("api", __name__)

@api_bp.route("/get_stock", methods=["GET"])
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

