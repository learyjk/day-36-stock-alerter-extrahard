import requests
from config import *
from datetime import datetime
from twilio.rest import Client

STOCK = "TSLA"
COMPANY_NAME = "Tesla Inc"
PERCENT_THRESHOLD = 0.005


def get_news():
    news_params = {
        "q": COMPANY_NAME,
        "from": datetime.now(),
        "sortby": "popularity",
        "apikey": API_KEY_NEWS,
    }

    url_news = "http://newsapi.org/v2/everything"

    response_news = requests.get(url_news, params=news_params)
    response_news.raise_for_status()
    news_data = response_news.json()['articles']
    headlines = []
    for article in news_data:
        headlines.append(article['title'])
        if len(headlines) >= 3:
            break
    return headlines[0]


def send_text(percent, news_headline):
    client = Client(account_sid, auth_token)
    message = client.messages \
        .create(
            body=f"{STOCK} change {percent}%: {news_headline}",
            from_=FROM_NUM,
            to=TO_NUM
        )
    print(message.status)


def query_stock_change():
    av_params = {
        "function": "TIME_SERIES_DAILY",
        "symbol": STOCK,
        "outputsize": "compact",
        "apikey": API_KEY_ALPHAVANTAGE,
    }

    url_av = "https://www.alphavantage.co/query"

    response_av = requests.get(url_av, params=av_params)
    response_av.raise_for_status()
    stock_data = response_av.json()

    price_yesterday_close = float(list(stock_data['Time Series (Daily)'].values())[0]['4. close'])
    price_daybefore_yesterday_close = float(list(stock_data['Time Series (Daily)'].values())[1]['4. close'])

    diff = abs(price_daybefore_yesterday_close - price_yesterday_close)
    percent_change = diff/price_daybefore_yesterday_close
    return percent_change


change = query_stock_change()
if change > PERCENT_THRESHOLD:
    h = get_news()
    formatted_change = "{:.2f}".format(change)
    send_text(formatted_change, h)
