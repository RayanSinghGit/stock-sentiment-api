from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import yfinance as yf
from bs4 import BeautifulSoup
from textblob import TextBlob

app = Flask(__name__)
CORS(app)  # Allow frontend (Framer) to call the API

# Function to fetch stock news and sentimentdef get_stock_news(ticker):
from transformers import AutoModelForSequenceClassification, AutoTokenizer, pipeline

# Load FinBERT Model
model_name = "ProsusAI/finbert"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSequenceClassification.from_pretrained(model_name)
nlp = pipeline("sentiment-analysis", model=model, tokenizer=tokenizer)

# Function to Fetch Stock News and Analyze Sentiment
import requests
from bs4 import BeautifulSoup
from serpapi import GoogleSearch  # For Google News API
import os

# Use your free SerpAPI key here
SERPAPI_KEY = "c804f2de22e6c974412984a4075f169e03b1d21d32d62f06051ca59955ff75af"
BING_API_KEY = "YOUR_BING_API_KEY"  # Get from Microsoft Bing

def get_stock_news(ticker):
    news_data = []
    
    #  1. Get news from Google (via SerpAPI)
    try:
        params = {
            "engine": "google_news",
            "q": f"{ticker} stock",
            "api_key": SERPAPI_KEY,
            "num": 5  # Limit to top 5
        }
        search = GoogleSearch(params)
        results = search.get_dict()
        news_results = results.get("news_results", [])

        for article in news_results:
            news_data.append({
                "headline": article["title"],
                "link": article["link"],
                "source": "Google News"
            })
    except Exception as e:
        print(f"Google News error: {e}")

    #  2. Get news from Yahoo Finance (scraping)
    try:
        yahoo_url = f"https://finance.yahoo.com/quote/{ticker}/news"
        response = requests.get(yahoo_url, headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(response.text, 'html.parser')
        headlines = soup.select("h3 a")[:5]  # Top 5 headlines

        for h in headlines:
            text = h.get_text()
            link = "https://finance.yahoo.com" + h["href"]
            news_data.append({
                "headline": text,
                "link": link,
                "source": "Yahoo Finance"
            })
    except Exception as e:
        print(f"Yahoo Finance error: {e}")

# Function to fetch stock price and price target
def get_stock_data(ticker):
    try:
        stock = yf.Ticker(ticker)  # Fetch stock data
        stock_info = stock.history(period="5d")  # Get last 5 days of stock history

        if stock_info.empty:
            return {"error": "Invalid stock ticker or no data available"}

        return {
            "stock_name": stock.info.get('shortName', 'N/A'),
            "current_price": stock.info.get('regularMarketPrice', 'N/A'),
            "previous_close": stock.info.get('previousClose', 'N/A'),
            "market_cap": stock.info.get('marketCap', 'N/A'),
            "news": get_stock_news(ticker),
            "price_trend": stock_info['Close'].tolist() if not stock_info.empty else "N/A"
        }
    except Exception as e:
        return {"error": f"Failed to fetch stock data: {str(e)}"}

@app.route("/get_stock", methods=["GET"])
def stock_data():
    ticker = request.args.get("ticker", "").upper()
    if not ticker:
        return jsonify({"error": "Missing stock ticker"}), 400
    
    data = get_stock_data(ticker)
    return jsonify(data)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)


