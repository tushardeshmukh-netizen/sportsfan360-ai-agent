import requests
import json
import zipfile
import io
import os
import re
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from groq import Groq

DATA_URL = "https://cricsheet.org/downloads/ipl_json.zip"

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------- GROQ CLIENT ----------------

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    raise Exception("GROQ_API_KEY not set")

groq = Groq(api_key=GROQ_API_KEY)

# ---------------- DATA CACHES ----------------

matches_cache = None
runs_cache = {}
wickets_cache = {}
season_runs_cache = {}
highest_score_cache = None


# ---------------- STARTUP ----------------

@app.on_event("startup")
def startup_load():
    parse_dataset()


# ---------------- DOWNLOAD DATA ----------------

def download_dataset():
    r = requests.get(DATA_URL, timeout=60)
    return zipfile.ZipFile(io.BytesIO(r.content))


# ---------------- PARSE DATA ----------------

def parse_dataset():

    global matches_cache, runs_cache, wickets_cache, season_runs_cache, highest_score_cache

    if matches_cache:
        return

    zip_file = download_dataset()

    matches = []
    batsman_runs = {}
    bowler_wickets = {}
    season_runs = {}

    highest_score = {"runs": 0, "player": None, "match": None}

    for file in zip_file.namelist():

        if not file.endswith(".json"):
            continue

        try:

            match_json = json.loads(zip_file.read(file))

            info = match_json.get("info", {})
            season = str(info.get("season"))
            teams = info.get("teams", [None, None])
            winner = info.get("outcome", {}).get("winner")

            matches.append({
                "season": season,
                "team1": teams[0],
                "team2": teams[1],
                "winner": winner
            })

            if season not in season_runs:
                season_runs[season] = {}

            match_runs = {}

            innings = match_json.get("innings", [])

            for inn in innings:

                for over in inn.get("overs", []):

                    for d in over.get("deliveries", []):

                        batter = d.get("batter")
                        bowler = d.get("bowler")
                        runs = d.get("runs", {}).get("batter", 0)

                        if batter:
                            batsman_runs[batter] = batsman_runs.get(batter, 0) + runs
                            match_runs[batter] = match_runs.get(batter, 0) + runs
                            season_runs[season][batter] = season_runs[season].get(batter, 0) + runs

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

        except:
            continue

    matches_cache = matches
    runs_cache = batsman_runs
    wickets_cache = bowler_wickets
    season_runs_cache = season_runs
    highest_score_cache = highest_score


# ---------------- UTIL FUNCTIONS ----------------

def top_players(stats, n=10):
    sorted_players = sorted(stats.items(), key=lambda x: x[1], reverse=True)
    return [{"player": p, "value": v} for p, v in sorted_players[:n]]


def compute_titles():

    titles = {}

    for m in matches_cache:
        if m["winner"]:
            titles[m["winner"]] = titles.get(m["winner"], 0) + 1

    sorted_titles = sorted(titles.items(), key=lambda x: x[1], reverse=True)

    return [{"player": t, "value": c} for t, c in sorted_titles]


def compare_players(p1, p2):

    r1 = runs_cache.get(p1, 0)
    r2 = runs_cache.get(p2, 0)

    leader = p1 if r1 > r2 else p2

    return {
        "chart_title": f"{p1} vs {p2} IPL Runs",
        "chart_data": [
            {"player": p1, "value": r1},
            {"player": p2, "value": r2}
        ],
        "answer": f"{leader} leads with more IPL runs."
    }


# ---------------- PLAYER MATCHING ----------------

def detect_players(question):

    q = question.lower()
    found = []

    for p in runs_cache.keys():

        parts = p.lower().split()

        for part in parts:
            if part in q:
                found.append(p)
                break

    return list(set(found))


# ---------------- LLM EXPLANATION ----------------

def llm_answer(question):

    try:

        response = groq.chat.completions.create(
            model="llama3-70b-8192",
            messages=[
                {
                    "role": "system",
                    "content": "You are a cricket analyst who answers IPL related questions clearly and in detail."
                },
                {
                    "role": "user",
                    "content": question
                }
            ],
            temperature=0.3
        )

        return response.choices[0].message.content

    except Exception:
        return "Unable to fetch AI response at the moment."


# ---------------- MAIN AGENT ----------------

def run_agent(question):

    q = question.lower()

    players = detect_players(q)

    # PLAYER COMPARISON
    if "compare" in q or "vs" in q:

        if len(players) >= 2:
            return compare_players(players[0], players[1])

    # TOP RUNS
    if "run" in q:

        data = top_players(runs_cache)

        return {
            "chart_title": "Top Run Scorers IPL History",
            "chart_data": data,
            "answer": f"{data[0]['player']} has scored the most runs in IPL history with {data[0]['value']} runs."
        }

    # TOP WICKETS
    if "wicket" in q:

        data = top_players(wickets_cache)

        return {
            "chart_title": "Top Wicket Takers IPL",
            "chart_data": data,
            "answer": f"{data[0]['player']} has taken the most wickets in IPL history with {data[0]['value']} wickets."
        }

    # TEAM TITLES
    if "title" in q or "champion" in q:

        data = compute_titles()

        return {
            "chart_title": "Most IPL Titles",
            "chart_data": data,
            "answer": f"{data[0]['player']} has won the most IPL titles with {data[0]['value']} championships."
        }

    # HIGHEST SCORE
    if "highest" in q and "score" in q:

        return {
            "chart_title": "Highest IPL Individual Score",
            "chart_data": [
                {
                    "player": highest_score_cache["player"],
                    "value": highest_score_cache["runs"]
                }
            ],
            "answer": f"{highest_score_cache['player']} scored {highest_score_cache['runs']} runs in {highest_score_cache['match']}."
        }

    # FALLBACK → LLM
    answer = llm_answer(question)

    return {
        "chart_title": "",
        "chart_data": [],
        "answer": answer
    }


# ---------------- API ----------------

@app.get("/")
def home():
    return {"message": "SportsFan360 AI Agent running"}


@app.get("/ask")
def ask(question: str):

    try:
        return run_agent(question)

    except Exception as e:

        return {
            "chart_title": "",
            "chart_data": [],
            "answer": str(e)
        }
