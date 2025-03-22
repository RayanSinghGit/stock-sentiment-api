from flask import Flask, request, jsonify
from flask_cors import CORS
import yfinance as yf
import requests
import matplotlib.pyplot as plt
import pandas as pd
import os
from textblob import TextBlob
import math

from api.ticker_lookup import search_stocks  # ✅ uses your existing file

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

NEWS_API_KEY = "YOUR_NEWS_API_KEY"  # Replace with your News API Key


def safe_number(value, default=0):
    return value if isinstance(value, (int, float)) and not math.isnan(value) else default


def calculate_rsi(hist, period=14):
    delta = hist['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))


def get_stock_data(ticker):
    stock = yf.Ticker(ticker)
    hist = stock.history(period="6mo")

    if hist.empty:
        return None

    stock_info = stock.info

    sma_50 = safe_number(hist['Close'].rolling(window=50).mean().dropna().iloc[-1] if len(hist) >= 50 else None)
    sma_100 = safe_number(hist['Close'].rolling(window=100).mean().dropna().iloc[-1] if len(hist) >= 100 else None)
    sma_200 = safe_number(hist['Close'].rolling(window=200).mean().dropna().iloc[-1] if len(hist) >= 200 else None)

    return {
        "stock_name": stock_info.get("longName", ticker),
        "current_price": stock_info.get("currentPrice"),
        "previous_close": stock_info.get("previousClose"),
        "market_cap": stock_info.get("marketCap"),
        "pe_ratio": stock_info.get("trailingPE"),
        "pb_ratio": stock_info.get("priceToBook"),
        "eps": stock_info.get("trailingEps"),
        "sma_50": round(sma_50, 2),
        "sma_100": round(sma_100, 2),
        "sma_200": round(sma_200, 2),
        "croci": stock_info.get("returnOnEquity"),
        "rsi_14": round(safe_number(calculate_rsi(hist).iloc[-1]), 2),
        "price_trend": list(hist['Close'].tail(5)),
    }


def get_latest_news(ticker):
    url = f"https://newsapi.org/v2/everything?q={ticker}&sortBy=relevancy&language=en&apiKey={NEWS_API_KEY}"
    response = requests.get(url)

    if response.status_code != 200:
        return {"news": [], "sentiment_score": 0}

    articles = response.json().get("articles", [])[:10]
    news_data = []
    total_score = 0

    for article in articles:
        headline = article["title"]
        sentiment_score = TextBlob(headline).sentiment.polarity
        total_score += sentiment_score
        sentiment_label = (
            "positive" if sentiment_score > 0 else "negative" if sentiment_score < 0 else "neutral"
        )

        news_data.append({
            "headline": headline,
            "url": article["url"],
            "sentiment": sentiment_label
        })

    avg_sentiment = round(total_score / len(articles), 2) if articles else 0

    return {"news": news_data, "sentiment_score": avg_sentiment}


@app.route("/api/search_ticker", methods=["GET"])
def search_ticker():
    query = request.args.get("query", "")
    if not query:
        return jsonify([])

    results = search_stocks(query)
    return jsonify(results)


@app.route("/api/get_stock", methods=["GET"])
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


@app.after_request
def add_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    return response


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000, debug=True)

