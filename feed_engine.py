import requests
import os
import random

NEWS_API_KEY = os.getenv("e9483687581d4fb39447352f50c42dbb")

NEWS_URL = "https://newsapi.org/v2/everything"


def get_feed():

    try:

        params = {
            "q": "IPL OR cricket",
            "language": "en",
            "sortBy": "publishedAt",
            "pageSize": 6,
            "apiKey": NEWS_API_KEY
        }

        res = requests.get(NEWS_URL, params=params)
        data = res.json()

        cards = []

        for article in data["articles"][:6]:

            cards.append({
                "type": "news",
                "title": article["title"],
                "text": article["description"] or "Latest cricket news update",
                "image": article["urlToImage"],
                "link": article["url"]
            })

        return {"cards": cards}

    except Exception as e:

        return {
            "cards": [
                {
                    "type": "news",
                    "title": "IPL Season Updates",
                    "text": "Live cricket insights and match analysis",
                    "image": "https://upload.wikimedia.org/wikipedia/en/2/2e/Indian_Premier_League_Logo.svg",
                    "link": "https://www.iplt20.com"
                }
            ]
        }