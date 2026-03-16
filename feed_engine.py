import requests
import feedparser
import random

NEWS_API_KEY = "e9483687581d4fb39447352f50c42dbb"

NEWS_URL = "https://newsapi.org/v2/everything"

RSS_SOURCES = [

    "https://news.google.com/rss/search?q=IPL+cricket&hl=en-IN&gl=IN&ceid=IN:en",

    "https://www.espncricinfo.com/rss/content/story/feeds/0.xml",

    "https://www.icc-cricket.com/rss/media-releases"

]


def get_newsapi_cards():

    cards = []

    try:

        params = {
            "q": "IPL OR cricket",
            "language": "en",
            "sortBy": "publishedAt",
            "pageSize": 6,
            "apiKey": NEWS_API_KEY
        }

        res = requests.get(NEWS_URL, params=params, timeout=5)

        data = res.json()

        for article in data.get("articles", []):

            cards.append({
                "type": "news",
                "title": article.get("title"),
                "text": article.get("description") or "Latest cricket news",
                "image": article.get("urlToImage"),
                "link": article.get("url")
            })

    except Exception:
        pass

    return cards


def get_rss_cards():

    cards = []

    for url in RSS_SOURCES:

        try:

            feed = feedparser.parse(url)

            for entry in feed.entries[:4]:

                image = None

                if "media_content" in entry:
                    image = entry.media_content[0]["url"]

                if not image and "links" in entry:
                    for l in entry.links:
                        if "image" in str(l.get("type")):
                            image = l.get("href")

                cards.append({
                    "type": "news",
                    "title": entry.get("title"),
                    "text": entry.get("summary", "Latest cricket news"),
                    "image": image,
                    "link": entry.get("link")
                })

        except Exception:
            continue

    return cards


def get_feed():

    cards = []

    # NewsAPI source
    cards.extend(get_newsapi_cards())

    # RSS sources
    cards.extend(get_rss_cards())

    # remove duplicates
    unique = []
    titles = set()

    for c in cards:
        if c["title"] not in titles:
            unique.append(c)
            titles.add(c["title"])

    # shuffle for variety
    random.shuffle(unique)

    # limit feed size
    final_cards = unique[:12]

    if not final_cards:

        final_cards = [
            {
                "type": "news",
                "title": "IPL Season Updates",
                "text": "Latest cricket insights and match updates",
                "image": "https://upload.wikimedia.org/wikipedia/en/2/2e/Indian_Premier_League_Logo.svg",
                "link": "https://www.iplt20.com"
            }
        ]

    return {"cards": final_cards}