import requests

API_KEY = "830cd356-c66b-4f9a-9fcb-40ed04fae5b5"

def get_live_matches():

    try:
        # 🔥 1. CURRENT MATCHES
        match_url = f"https://api.cricapi.com/v1/currentMatches?apikey={API_KEY}&offset=0"
        match_res = requests.get(match_url, timeout=10)
        match_data = match_res.json().get("data", [])

        # 🔥 2. SCORE DATA
        score_url = f"https://api.cricapi.com/v1/cricScore?apikey={API_KEY}"
        score_res = requests.get(score_url, timeout=10)
        score_data = score_res.json().get("data", [])

        matches = []

        for m in match_data:

            team_info = m.get("teamInfo", [])
            team1 = team_info[0].get("name", "TBD") if len(team_info) > 0 else "TBD"
            team2 = team_info[1].get("name", "TBD") if len(team_info) > 1 else "TBD"

            status = m.get("status", "Upcoming")

            # 🔥 MATCH SCORE LINKING
            score_text = ""
            for s in score_data:
                if team1 in s.get("t1", "") and team2 in s.get("t2", ""):
                    score_text = s.get("score", "")
                    break

            matches.append({
                "id": m.get("id"),
                "team1": team1,
                "team2": team2,
                "status": status,
                "venue": m.get("venue", "Unknown"),
                "date": m.get("date", ""),
                "score": score_text if score_text else "No score yet"
            })

        # 🔥 SORT LIVE FIRST
        matches = sorted(matches, key=lambda x: (
            "live" not in x["status"].lower()
        ))

        return matches[:10]

    except Exception as e:
        print("Match Error:", e)
        return get_dummy_matches()


def get_dummy_matches():
    return [
        {
            "id": "demo1",
            "team1": "CSK",
            "team2": "MI",
            "status": "Live",
            "venue": "Wankhede",
            "date": "Today",
            "score": "CSK 145/3 (15.2)"
        },
        {
            "id": "demo2",
            "team1": "RCB",
            "team2": "KKR",
            "status": "Upcoming",
            "venue": "Chinnaswamy",
            "date": "Today",
            "score": "Starts at 7:30 PM"
        }
    ]