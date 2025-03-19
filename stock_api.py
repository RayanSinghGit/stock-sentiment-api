from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import yfinance as yf
from bs4 import BeautifulSoup
from textblob import TextBlob

app = Flask(__name__)
CORS(app)  # Allow frontend (Framer) to call the API

# Function to fetch stock news and sentiment
def get_stock_news(ticker):
    url = f"https://news.google.com/search?q={ticker}%20stock"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    headlines = soup.find_all('h3')[:5]  # Get top 5 headlines
    news_data = []
    
    for h in headlines:
        text = h.get_text()
        sentiment = TextBlob(text).sentiment.polarity  # Sentiment Analysis
        news_data.append({"headline": text, "sentiment": "Bullish" if sentiment > 0 else "Bearish" if sentiment < 0 else "Neutral"})

    return news_data

# Function to fetch stock price and price target
import requests
import yfinance as yf

def get_stock_data(ticker):
    session = requests.Session()
    session.headers.update({'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})  # Spoof browser
    stock = yf.Ticker(ticker, session=session)

    try:
        return {
            "stock_name": stock.info.get('shortName', 'N/A'),
            "current_price": stock.info.get('regularMarketPrice', 'N/A'),
            "previous_close": stock.info.get('previousClose', 'N/A'),
            "market_cap": stock.info.get('marketCap', 'N/A')
        }
    except Exception as e:
        return {"error": f"Failed to fetch stock data: {str(e)}"}

    stock_info = stock.history(period="5d")
    
    return {
        "stock_name": stock.info.get('shortName', 'N/A'),
        "current_price": round(stock_info['Close'][-1], 2) if not stock_info.empty else "N/A",
        "news": get_stock_news(ticker)
    }

@app.route("/get_stock", methods=["GET"])
def stock_data():
    ticker = request.args.get("ticker", "").upper()
    if not ticker:
        return jsonify({"error": "Missing stock ticker"}), 400
    
    data = get_stock_data(ticker)
    return jsonify(data)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

