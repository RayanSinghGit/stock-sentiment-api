import matplotlib.pyplot as plt
import yfinance as yf
from flask import send_file
from io import BytesIO

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

    return send_file(img, mimetype='image/png')

