import requests

API_KEY = "830cd356-c66b-4f9a-9fcb-40ed04fae5b5"

def get_live_matches():

    url = f"https://api.cricapi.com/v1/currentMatches?apikey={API_KEY}&offset=0"

    try:
        res = requests.get(url, timeout=10)

        if res.status_code != 200:
            print("API ERROR:", res.status_code, res.text)
            return get_dummy_matches()

        data = res.json()

        # 🔥 IMPORTANT: cricapi uses "data"
        matches_data = data.get("data", [])

        matches = []

        for m in matches_data:

            team1 = m.get("teamInfo", [{}])[0].get("name", "TBD") if len(m.get("teamInfo", [])) > 0 else "TBD"
            team2 = m.get("teamInfo", [{}])[1].get("name", "TBD") if len(m.get("teamInfo", [])) > 1 else "TBD"

            status = m.get("status", "Upcoming")

            if not team1 or not team2:
                continue

            matches.append({
                "id": m.get("id"),
                "team1": team1,
                "team2": team2,
                "status": status,
                "venue": m.get("venue", "Unknown"),
                "date": m.get("date", "")
            })

        # 🔥 SORT: LIVE FIRST
        matches = sorted(matches, key=lambda x: (
            "live" not in x["status"].lower() and "progress" not in x["status"].lower()
        ))

        # 🔥 LIMIT
        matches = matches[:10]

        if len(matches) == 0:
            return get_dummy_matches()

        return matches

    except Exception as e:
        print("Live Match Error:", e)
        return get_dummy_matches()


# 🔥 FALLBACK
def get_dummy_matches():
    return [
        {
            "id": "demo1",
            "team1": "CSK",
            "team2": "MI",
            "status": "Match in progress",
            "venue": "Wankhede Stadium",
            "date": "Today"
        },
        {
            "id": "demo2",
            "team1": "RCB",
            "team2": "KKR",
            "status": "Starting soon",
            "venue": "Chinnaswamy",
            "date": "Today"
        }
    ]