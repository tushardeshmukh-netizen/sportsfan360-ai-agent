import requests

API_KEY = "830cd356-c66b-4f9a-9fcb-40ed04fae5b5"

def get_live_matches():

    url = f"https://api.cricketdata.org/v1/matches?apikey={API_KEY}"

    try:
        res = requests.get(url, timeout=10)

        if res.status_code != 200:
            print("API ERROR:", res.status_code, res.text)
            return get_dummy_matches()

        data = res.json()

        matches = []

        for m in data.get("data", []):

            teams = m.get("teams", [])

            team1 = teams[0] if len(teams) > 0 else "TBD"
            team2 = teams[1] if len(teams) > 1 else "TBD"

            status = m.get("status", "Upcoming")

            # 🔥 FILTER ONLY USEFUL MATCHES
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

        # 🔥 SORT: LIVE FIRST, THEN UPCOMING
        matches = sorted(matches, key=lambda x: (
            "live" not in x["status"].lower(),
            "progress" not in x["status"].lower()
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