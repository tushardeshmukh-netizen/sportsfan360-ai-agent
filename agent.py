import requests
import json
import zipfile
import io
import re
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

DATA_URL = "https://cricsheet.org/downloads/ipl_json.zip"

app = FastAPI()

# CORS for Vercel frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

matches_cache = None
runs_cache = None
wickets_cache = None
pom_cache = None
highest_score_cache = None


@app.on_event("startup")
def startup_load():
    parse_dataset()


def download_dataset():

    print("Downloading IPL dataset...")

    r = requests.get(DATA_URL, timeout=60)

    return zipfile.ZipFile(io.BytesIO(r.content))


def parse_dataset():

    global matches_cache, runs_cache, wickets_cache, pom_cache, highest_score_cache

    if matches_cache:
        return

    zip_file = download_dataset()

    matches = []
    batsman_runs = {}
    bowler_wickets = {}
    player_of_match = {}

    highest_score = {
        "runs": 0,
        "player": None,
        "match": None
    }

    for file in zip_file.namelist():

        if not file.endswith(".json"):
            continue

        try:

            match_json = json.loads(zip_file.read(file))

            info = match_json.get("info", {})
            season = info.get("season")
            teams = info.get("teams", [None, None])
            winner = info.get("outcome", {}).get("winner")
            pom = info.get("player_of_match", [])

            matches.append({
                "season": season,
                "team1": teams[0],
                "team2": teams[1],
                "winner": winner
            })

            for p in pom:
                player_of_match[p] = player_of_match.get(p, 0) + 1

            match_runs = {}

            innings = match_json.get("innings", [])

            for inn in innings:

                overs = inn.get("overs", [])

                for over in overs:

                    deliveries = over.get("deliveries", [])

                    for d in deliveries:

                        batter = d.get("batter")
                        bowler = d.get("bowler")

                        runs = d.get("runs", {}).get("batter", 0)

                        if batter:
                            batsman_runs[batter] = batsman_runs.get(batter, 0) + runs
                            match_runs[batter] = match_runs.get(batter, 0) + runs

                        wickets = d.get("wickets", [])

                        if wickets and bowler:
                            bowler_wickets[bowler] = bowler_wickets.get(bowler, 0) + len(wickets)

            for player, r in match_runs.items():

                if r > highest_score["runs"]:
                    highest_score = {
                        "runs": r,
                        "player": player,
                        "match": f"{teams[0]} vs {teams[1]} ({season})"
                    }

        except Exception as e:
            print("Error parsing match:", e)
            continue

    matches_cache = matches
    runs_cache = batsman_runs
    wickets_cache = bowler_wickets
    pom_cache = player_of_match
    highest_score_cache = highest_score


def top_players(stats, n=10):

    sorted_players = sorted(stats.items(), key=lambda x: x[1], reverse=True)

    return [
        {"player": p, "value": v}
        for p, v in sorted_players[:n]
    ]


def compute_titles():

    titles = {}

    for m in matches_cache:

        if m["winner"]:
            titles[m["winner"]] = titles.get(m["winner"], 0) + 1

    sorted_titles = sorted(titles.items(), key=lambda x: x[1], reverse=True)

    return [
        {"team": t, "titles": c}
        for t, c in sorted_titles
    ]


@app.get("/")
def home():
    return {"message": "SportsFan360 IPL AI Agent running"}


@app.get("/ask")
def ask(question: str):

    parse_dataset()

    q = question.lower()

    # Top run scorers
    if "run" in q or "scorer" in q:
        return {"top_run_scorers": top_players(runs_cache)}

    # Most wickets
    if "wicket" in q:
        return {"top_wicket_takers": top_players(wickets_cache)}

    # Highest score
    if "highest score" in q:
        return {"highest_score": highest_score_cache}

    # Player of match leaders
    if "player of match" in q:
        return {"top_player_of_match": top_players(pom_cache)}

    # IPL winner by year
    year = re.findall(r"\d{4}", q)

    if year:
        year = int(year[0])

        for m in matches_cache:
            if str(m["season"]) == str(year):
                return {
                    "season": year,
                    "winner": m["winner"]
                }

    return {"message": "Question not understood"}
