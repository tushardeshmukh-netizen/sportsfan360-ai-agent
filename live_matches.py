import requests

API_KEY = "830cd356-c66b-4f9a-9fcb-40ed04fae5b5"

def get_live_matches():

    try:
        # 🔥 1. LIVE / CURRENT MATCHES
        current_url = f"https://api.cricapi.com/v1/currentMatches?apikey={API_KEY}&offset=0"
        current_res = requests.get(current_url, timeout=10)
        current_data = current_res.json().get("data", [])

        # 🔥 2. ALL MATCHES (UPCOMING INCLUDED)
        matches_url = f"https://api.cricapi.com/v1/matches?apikey={API_KEY}&offset=0"
        matches_res = requests.get(matches_url, timeout=10)
        all_matches_data = matches_res.json().get("data", [])

        # 🔥 3. SCORE DATA
        score_url = f"https://api.cricapi.com/v1/cricScore?apikey={API_KEY}"
        score_res = requests.get(score_url, timeout=10)
        score_data = score_res.json().get("data", [])

        print("CURRENT:", len(current_data))
        print("ALL MATCHES:", len(all_matches_data))
        print("SCORES:", len(score_data))

        matches = []

        # 🔥 HELPER: EXTRACT TEAMS
        def extract_teams(m):
            team_info = m.get("teamInfo", [])
            if len(team_info) >= 2:
                return team_info[0].get("name", "TBD"), team_info[1].get("name", "TBD")
            return None, None

        # 🔥 HELPER: MATCH SCORE
        def get_score(team1, team2):
            for s in score_data:
                t1 = s.get("t1", "").lower()
                t2 = s.get("t2", "").lower()

                if team1.lower() in t1 or team2.lower() in t2:
                    return s.get("score", "")
            return "No score yet"

        # 🔥 1. ADD LIVE MATCHES FIRST
        for m in current_data:
            team1, team2 = extract_teams(m)
            if not team1 or not team2:
                continue

            matches.append({
                "id": m.get("id"),
                "team1": team1,
                "team2": team2,
                "status": m.get("status", "Live"),
                "venue": m.get("venue", "Unknown"),
                "date": m.get("date", ""),
                "score": get_score(team1, team2)
            })

        # 🔥 2. ADD UPCOMING MATCHES (IF LESS THAN 10)
        for m in all_matches_data:

            if len(matches) >= 10:
                break

            team1, team2 = extract_teams(m)
            if not team1 or not team2:
                continue

            # ❌ skip duplicates
            already_exists = any(
                x["team1"] == team1 and x["team2"] == team2
                for x in matches
            )

            if already_exists:
                continue

            matches.append({
                "id": m.get("id"),
                "team1": team1,
                "team2": team2,
                "status": m.get("status", "Upcoming"),
                "venue": m.get("venue", "Unknown"),
                "date": m.get("date", ""),
                "score": "Starts soon"
            })

        # 🔥 FINAL SORT → LIVE FIRST
        matches = sorted(matches, key=lambda x: (
            "live" not in x["status"].lower()
        ))

        return matches[:10]

    except Exception as e:
        print("Match Error:", e)

        # 🔥 HARD FAIL SAFE (MINIMAL)
        return [
            {
                "id": "fallback1",
                "team1": "India",
                "team2": "Australia",
                "status": "Data unavailable",
                "venue": "Check API",
                "date": "",
                "score": "Try again"
            }
        ]