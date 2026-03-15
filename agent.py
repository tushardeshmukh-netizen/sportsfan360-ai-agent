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

groq = Groq(api_key=os.getenv("GROQ_API_KEY"))

dataset_loaded = False

player_runs = {}
player_balls = {}
player_outs = {}
player_wickets = {}

team_wins = {}
team_matches = {}

titles_cache = {}
highest_score_cache = {}
player_index = {}

TEAM_ALIASES = {
    "royal challengers bengaluru": "Royal Challengers Bangalore",
    "rcb": "Royal Challengers Bangalore",
    "kings xi punjab": "Punjab Kings",
    "delhi daredevils": "Delhi Capitals",
}

def normalize_team(name):
    if not name:
        return name
    key = name.lower()
    return TEAM_ALIASES.get(key, name)


def load_dataset():

    global dataset_loaded
    global highest_score_cache
    global titles_cache

    if dataset_loaded:
        return

    titles_cache = {}

    r = requests.get(DATA_URL, timeout=120)
    zip_file = zipfile.ZipFile(io.BytesIO(r.content))

    highest = {"runs": 0, "player": None, "match": None}

    for file in zip_file.namelist():

        if not file.endswith(".json"):
            continue

        try:

            match = json.loads(zip_file.read(file))
            info = match.get("info", {})

            teams = info.get("teams", [None, None])
            season = str(info.get("season"))
            winner = normalize_team(info.get("outcome", {}).get("winner"))

            teams = [normalize_team(t) for t in teams]

            # IPL FINAL DETECTION
            event = info.get("event", {})
            match_number = str(event.get("match_number", "")).lower()

            if "final" in match_number and winner:
                titles_cache[winner] = titles_cache.get(winner, 0) + 1

            for t in teams:
                if t:
                    team_matches[t] = team_matches.get(t, 0) + 1

            if winner:
                team_wins[winner] = team_wins.get(winner, 0) + 1

            match_runs = {}

            for inn in match.get("innings", []):
                for over in inn.get("overs", []):
                    for d in over.get("deliveries", []):

                        batter = d.get("batter")
                        bowler = d.get("bowler")
                        runs = d.get("runs", {}).get("batter", 0)

                        if batter:

                            player_runs[batter] = player_runs.get(batter, 0) + runs
                            player_balls[batter] = player_balls.get(batter, 0) + 1
                            match_runs[batter] = match_runs.get(batter, 0) + runs

                            for p in batter.lower().split():
                                player_index.setdefault(p, set()).add(batter)

                        wickets = d.get("wickets", [])

                        if wickets and bowler:
                            player_wickets[bowler] = player_wickets.get(bowler, 0) + len(wickets)

                        if wickets and batter:
                            player_outs[batter] = player_outs.get(batter, 0) + 1

            for p, r in match_runs.items():
                if r > highest["runs"]:
                    highest = {
                        "runs": r,
                        "player": p,
                        "match": f"{teams[0]} vs {teams[1]} ({season})"
                    }

        except:
            continue

    highest_score_cache = highest
    dataset_loaded = True


# -------- TOOLS --------

def top_runs():
    data = sorted(player_runs.items(), key=lambda x: x[1], reverse=True)[:10]
    return {
        "chart_title": "Top IPL Run Scorers",
        "chart_data": [{"player": p, "value": v} for p, v in data],
        "answer": f"{data[0][0]} leads IPL run scoring."
    }


def top_wickets():
    data = sorted(player_wickets.items(), key=lambda x: x[1], reverse=True)[:10]
    return {
        "chart_title": "Top IPL Wicket Takers",
        "chart_data": [{"player": p, "value": v} for p, v in data],
        "answer": f"{data[0][0]} has taken the most IPL wickets."
    }


def team_titles():
    data = sorted(titles_cache.items(), key=lambda x: x[1], reverse=True)
    return {
        "chart_title": "Most IPL Titles",
        "chart_data": [{"player": t, "value": c} for t, c in data],
        "answer": f"{data[0][0]} has won the most IPL titles."
    }


def strike_rate(player):

    runs = player_runs.get(player, 0)
    balls = player_balls.get(player, 1)
    sr = round((runs / balls) * 100, 2)

    return {
        "chart_title": "Strike Rate",
        "chart_data": [{"player": player, "value": sr}],
        "answer": f"{player}'s strike rate is {sr}"
    }


def batting_average(player):

    runs = player_runs.get(player, 0)
    outs = player_outs.get(player, 1)
    avg = round(runs / outs, 2)

    return {
        "chart_title": "Batting Average",
        "chart_data": [{"player": player, "value": avg}],
        "answer": f"{player}'s IPL average is {avg}"
    }


def highest_score():
    return {
        "chart_title": "Highest IPL Score",
        "chart_data": [{"player": highest_score_cache["player"], "value": highest_score_cache["runs"]}],
        "answer": f"{highest_score_cache['player']} scored {highest_score_cache['runs']} in {highest_score_cache['match']}"
    }


def detect_players(q):

    tokens = re.findall(r"[a-z]+", q.lower())
    found = set()

    for t in tokens:
        if t in player_index:
            found.update(player_index[t])

    return list(found)


def compare_players(players):

    p1, p2 = players[:2]

    r1 = player_runs.get(p1, 0)
    r2 = player_runs.get(p2, 0)

    return {
        "chart_title": f"{p1} vs {p2}",
        "chart_data": [
            {"player": p1, "value": r1},
            {"player": p2, "value": r2}
        ],
        "answer": f"{p1 if r1 > r2 else p2} has scored more runs."
    }


# -------- TOOL PLANNER --------

def choose_tool(question):

    try:

        res = groq.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{
                "role": "user",
                "content": f"""
Choose best tool.

TOOLS:
top_runs
top_wickets
team_titles
strike_rate
batting_average
highest_score
compare_players
knowledge

Return JSON like:
{{"tool":"tool_name"}}

Question: {question}
"""
            }],
            temperature=0
        )

        text = res.choices[0].message.content.strip()
        data = json.loads(text)

        return data["tool"]

    except:

        q = question.lower()

        if "title" in q:
            return "team_titles"
        if "wicket" in q:
            return "top_wickets"
        if "run" in q:
            return "top_runs"

        return "knowledge"


def knowledge(question):

    try:

        res = groq.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You are an IPL cricket expert."},
                {"role": "user", "content": question}
            ]
        )

        answer = res.choices[0].message.content

    except:

        answer = (
            "The IPL is popular because it combines international cricket stars, "
            "fast-paced T20 matches, strong team rivalries, huge fan engagement, "
            "and massive TV and digital audiences."
        )

    return {
        "chart_title": "",
        "chart_data": [],
        "answer": answer
    }


# -------- AGENT --------

def run_agent(question):

    tool = choose_tool(question)
    players = detect_players(question)

    if tool == "top_runs":
        return top_runs()

    if tool == "top_wickets":
        return top_wickets()

    if tool == "team_titles":
        return team_titles()

    if tool == "highest_score":
        return highest_score()

    if tool == "strike_rate" and players:
        return strike_rate(players[0])

    if tool == "batting_average" and players:
        return batting_average(players[0])

    if tool == "compare_players" and len(players) >= 2:
        return compare_players(players)

    return knowledge(question)


@app.on_event("startup")
def startup():
    load_dataset()


@app.get("/")
def home():
    return {"message": "SportsFan360 AI running"}


@app.get("/ask")
def ask(question: str):
    return run_agent(question)
