import requests
import os

API_KEY = os.getenv("CRICKET_API_KEY")

def get_live_matches():

    url = f"https://api.cricketdata.org/v1/matches?apikey={830cd356-c66b-4f9a-9fcb-40ed04fae5b5}&status=live"

    try:
        res = requests.get(url, timeout=10)
        data = res.json()

        matches = []

        for m in data.get("data", []):

            matches.append({
                "id": m.get("id"),
                "team1": m.get("team1"),
                "team2": m.get("team2"),
                "status": m.get("status"),
                "venue": m.get("venue"),
                "date": m.get("date")
            })

        return matches

    except Exception as e:
        print("Live API Error:", e)
        return []