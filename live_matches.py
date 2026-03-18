import requests

# 🔥 PUT YOUR API KEY HERE
API_KEY = "830cd356-c66b-4f9a-9fcb-40ed04fae5b5"

def get_live_matches():

    url = f"https://api.cricketdata.org/v1/matches?apikey={API_KEY}"

    try:
        res = requests.get(url, timeout=10)

        if res.status_code != 200:
            print("API Error:", res.status_code, res.text)
            return []

        data = res.json()

        matches = []

        for m in data.get("data", []):

            status = (m.get("status") or "").lower()

            # ✅ FILTER LIVE + IN-PROGRESS + RECENT MATCHES
            if (
                "live" in status or
                "in progress" in status or
                "innings" in status or
                "match starts" in status or
                "yet to begin" in status
            ):

                matches.append({
                    "id": m.get("id"),
                    "team1": m.get("team1"),
                    "team2": m.get("team2"),
                    "status": m.get("status"),
                    "venue": m.get("venue"),
                    "date": m.get("date")
                })

        # ✅ FALLBACK (if nothing matched, show few matches anyway)
        if len(matches) == 0:
            for m in data.get("data", [])[:5]:
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