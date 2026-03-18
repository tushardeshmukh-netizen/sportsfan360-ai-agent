import requests

API_KEY = "830cd356-c66b-4f9a-9fcb-40ed04fae5b5"

def get_live_matches():

    url = f"https://api.cricketdata.org/v1/matches?apikey={API_KEY}"

    try:
        res = requests.get(url, timeout=10)

        if res.status_code != 200:
            print("API Error:", res.status_code)
            return []

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

        # ✅ ALWAYS RETURN SOMETHING
        return matches[:5]

    except Exception as e:
        print("Error:", e)
        return []