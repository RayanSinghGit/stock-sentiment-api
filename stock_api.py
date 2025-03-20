from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import yfinance as yf
import requests
import matplotlib.pyplot as plt
import pandas as pd
import os
from textblob import TextBlob
from io import BytesIO
import math

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

NEWS_API_KEY = "YOUR_NEWS_API_KEY"  # Replace with actual API Key

# Function to ensure numbers are valid and prevent NaN issues
def safe_number(value, default=0):
    """Returns the value if it's a number and not NaN, otherwise returns the default."""
    return value if isinstance(value, (int, float)) and not math.isnan(value) else default

# Function to fetch stock data
def get_stock_data(ticker):
    stock = yf.Ticker(ticker)
    hist = stock.history(period="6mo")  # Fetch 6-month history for the chart

    if hist.empty:
        return None

    # Fetching key financial metrics
    stock_info = stock.info

    # Fetching Simple Moving Averages (SMA) with safe defaults
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
        "croci": stock_info.get("returnOnEquity"),  # Approximate CROCI using ROE
        "price_trend": list(hist['Close'].tail(5)),  # Last 5 closing prices
    }

# Function to fetch news
def get_latest_news(ticker):
    url = f"https://newsapi.org/v2/everything?q={ticker}&sortBy=relevancy&language=en&apiKey={NEWS_API_KEY}"
    response = requests.get(url)

    if response.status_code != 200:
        return []

    articles = response.json().get("articles", [])[:10]  # Get top 10 articles
    news_data = []

    for article in articles:
        headline = article["title"]
        sentiment_score = TextBlob(headline).sentiment.polarity
        sentiment_label = "positive" if sentiment_score > 0 else "negative" if sentiment_score < 0 else "neutral"

        news_data.append({
            "headline": headline,
            "link": article["url"],
            "sentiment": sentiment_label
        })

    return news_data

# Function to generate stock price chart
def generate_stock_chart(ticker):
    stock = yf.Ticker(ticker)
    hist = stock.history(period="6mo")

    if hist.empty:
        return None

    plt.figure(figsize=(10, 5))
    plt.plot(hist.index, hist["Close"], label="Close Price", color="blue")
    plt.title(f"{ticker} Stock Price (Last 6 Months)")
    plt.xlabel("Date")
    plt.ylabel("Price (USD)")
    plt.legend()
    plt.grid()

    img = BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)

    return img

# API route to fetch stock data
@app.route("/get_stock", methods=["GET"])
def get_stock():
    ticker = request.args.get("ticker", "").upper()
    if not ticker:
        return jsonify({"error": "No ticker provided"}), 400

    stock_data = get_stock_data(ticker)
    if not stock_data:
        return jsonify({"error": "Invalid ticker or data unavailable"}), 400

    stock_data["news"] = get_latest_news(ticker)  # Add news data
    return jsonify(stock_data)

# API route to serve stock price chart
@app.route("/get_chart", methods=["GET"])
def get_chart():
    ticker = request.args.get("ticker", "").upper()
    if not ticker:
        return jsonify({"error": "No ticker provided"}), 400

    chart_img = generate_stock_chart(ticker)
    if not chart_img:
        return jsonify({"error": "Could not generate chart"}), 400

    return send_file(chart_img, mimetype='image/png')

# Enable CORS for all routes
@app.after_request
def add_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    return response

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000, debug=True)

