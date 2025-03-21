import requests
from textblob import TextBlob

NEWS_API_KEY = "YOUR_NEWS_API_KEY"  # Replace with an actual API key

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
            "link": article["url"],
            "sentiment": sentiment_label
        })

    avg_sentiment = round(total_score / len(articles), 2) if articles else 0

    return {"news": news_data, "sentiment_score": avg_sentiment}

