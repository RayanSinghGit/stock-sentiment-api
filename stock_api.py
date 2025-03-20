from flask import Flask, request, jsonify, send_file
import yfinance as yf
import requests
import matplotlib.pyplot as plt
import pandas as pd
import os
from textblob import TextBlob
from io import BytesIO

app = Flask(__name__)

NEWS_API_KEY = "YOUR_NEWS_API_KEY"  # Replace with actual API Key

# Function to fetch stock data
def get_stock_data(ticker):
    stock = yf.Ticker(ticker)
    
    hist = stock.history(period="6mo")  # Fetch 6-month history for the chart
    if hist.empty:
        return None
    
    # Fetching key financial metrics
    stock_info = stock.info
    ratios = stock.financials
    
    # Fetching Simple Moving Averages (SMA)
    sma_50 = hist['Close'].rolling(window=50).mean().iloc[-1]
    sma_100 = hist['Close'].rolling(window=100).mean().iloc[-1]
    sma_200 = hist['Close'].rolling(window=200).mean().iloc[-1]

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

if __name__ == "__main__":
    app.run(debug=True)

