import requests
import json
import zipfile
import io
import os
import random

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from groq import Groq

from stats_engine import *
from intent_router import detect_intent
from memory_store import save_context,get_context
from knowledge_base import get_player_info
from cricinfo_scraper import get_ipl_points_table
from cricket_api import get_live_matches
from feed_engine import get_feed
from teams_engine import get_teams
from players_engine import get_players
from matches_engine import get_matches
from standings_engine import get_standings
from daily_challenge import daily_challenge



DATA_URL="https://cricsheet.org/downloads/ipl_json.zip"

app.register_blueprint(daily_challenge)

app=FastAPI()

app.add_middleware(
CORSMiddleware,
allow_origins=["*"],
allow_credentials=True,
allow_methods=["*"],
allow_headers=["*"],
)

groq=Groq(api_key=os.getenv("GROQ_API_KEY"))

dataset_loaded=False

runs_cache={}
wickets_cache={}
titles_cache={}
highest_score_cache={}
sixes_cache={}
season_latest_match={}

# 🔥 FULL PLAYER + ADVANCED STATS
all_players=set()
balls_faced_cache={}
dismissals_cache={}
fours_cache={}
matches_played_cache={}

# 🔥 NAME NORMALIZATION
name_map={}

# 🔥 HUMAN FRIENDLY NAMES
player_alias = {
    "Virat Kohli": "V Kohli",
    "Rohit Sharma": "RG Sharma",
    "MS Dhoni": "MS Dhoni",
    "AB de Villiers": "AB de Villiers",
    "Chris Gayle": "CH Gayle",
    "KL Rahul": "KL Rahul",
    "Hardik Pandya": "HH Pandya",
    "Jasprit Bumrah": "JJ Bumrah",
    "Ravindra Jadeja": "RA Jadeja",
    "Suresh Raina": "SK Raina"
}

def build_name_map():
    global name_map
    name_map={}

    for p in runs_cache.keys():
        clean=p.lower().replace(".", "").strip()
        parts=clean.split()

        name_map[clean]=p

        if len(parts)>=2:
            name_map[parts[-1]]=p
            name_map[parts[0]+" "+parts[-1]]=p


def resolve_player(name):

    key = name.lower().replace(".", "").strip()

    if name in runs_cache:
        return name

    if key in name_map:
        return name_map[key]

    for full, short in player_alias.items():
        if key == full.lower():
            return short

    for p in runs_cache.keys():
        if key in p.lower():
            return p

    return name


# ---------------- DATASET LOADER ----------------

def load_dataset():

    global dataset_loaded,runs_cache,wickets_cache
    global highest_score_cache,sixes_cache
    global all_players
    global balls_faced_cache,dismissals_cache,fours_cache,matches_played_cache

    if dataset_loaded:
        return

    print("Loading IPL dataset...")

    r=requests.get(DATA_URL,timeout=120)
    zip_file=zipfile.ZipFile(io.BytesIO(r.content))

    batsman_runs={}
    bowler_wickets={}
    batsman_sixes={}
    balls_faced={}
    dismissals={}
    fours={}
    matches_played={}
    highest={"runs":0,"player":None}

    players_set=set()

    for file in zip_file.namelist():

        if not file.endswith(".json"):
            continue

        try:
            match=json.loads(zip_file.read(file))

            match_runs={}
            match_players=set()

            for inn in match.get("innings",[]):
                for over in inn.get("overs",[]):
                    for d in over.get("deliveries",[]):

                        batter=d.get("batter")
                        bowler=d.get("bowler")
                        runs=d.get("runs",{}).get("batter",0)

                        if batter:
                            players_set.add(batter)
                            match_players.add(batter)

                            batsman_runs[batter]=batsman_runs.get(batter,0)+runs
                            match_runs[batter]=match_runs.get(batter,0)+runs
                            balls_faced[batter]=balls_faced.get(batter,0)+1

                            if runs==4:
                                fours[batter]=fours.get(batter,0)+1
                            if runs==6:
                                batsman_sixes[batter]=batsman_sixes.get(batter,0)+1

                        if bowler:
                            players_set.add(bowler)
                            match_players.add(bowler)

                        wickets=d.get("wickets",[])

                        for w in wickets:
                            out=w.get("player_out")
                            if out:
                                players_set.add(out)
                                dismissals[out]=dismissals.get(out,0)+1

                        if wickets and bowler:
                            bowler_wickets[bowler]=bowler_wickets.get(bowler,0)+len(wickets)

            for p in match_players:
                matches_played[p]=matches_played.get(p,0)+1

            for p,runs in match_runs.items():
                if runs>highest["runs"]:
                    highest={"runs":runs,"player":p}

        except:
            continue

    all_players = players_set

    runs_cache=batsman_runs
    wickets_cache=bowler_wickets
    highest_score_cache=highest
    sixes_cache=batsman_sixes

    balls_faced_cache=balls_faced
    dismissals_cache=dismissals
    fours_cache=fours
    matches_played_cache=matches_played

    set_caches(runs_cache,wickets_cache,titles_cache,highest_score_cache,sixes_cache)

    build_name_map()

    dataset_loaded=True
    print("Dataset Loaded")


# ---------------- PLAYER LIST ----------------

@app.get("/player-list")
def player_list():
    load_dataset()

    players = set(all_players)

    reverse_alias = {v:k for k,v in player_alias.items()}

    clean_players=set()

    for p in players:
        if p in reverse_alias:
            clean_players.add(reverse_alias[p])
        else:
            clean_players.add(p)

    return {"players": sorted(list(clean_players))}


# ---------------- ASK API ----------------

@app.get("/ask")
def ask(question: str):

    try:
        load_dataset()
    except Exception as e:
        print("Dataset load error:", e)

    q = question.lower()

    # 🔥 SAFE CHECKS (important)
    if not runs_cache:
        return {
            "answer": "Data is still loading. Please try again in a few seconds.",
            "chart_title": "",
            "chart_data": []
        }

    # 🔥 BASIC INTENT HANDLING
    try:

        if "run" in q:
            top = max(runs_cache, key=runs_cache.get)
            return {
                "answer": f"{top} has the most IPL runs ({runs_cache[top]}).",
                "chart_title": "Most IPL Runs",
                "chart_data": []
            }

        elif "wicket" in q:
            top = max(wickets_cache, key=wickets_cache.get)
            return {
                "answer": f"{top} has taken the most IPL wickets ({wickets_cache[top]}).",
                "chart_title": "Most IPL Wickets",
                "chart_data": []
            }

        elif "six" in q:
            top = max(sixes_cache, key=sixes_cache.get)
            return {
                "answer": f"{top} has hit the most IPL sixes ({sixes_cache[top]}).",
                "chart_title": "Most IPL Sixes",
                "chart_data": []
            }

        elif "title" in q:
            # 🔥 FIX: fallback hardcoded
            return {
                "answer": "Mumbai Indians have won the most IPL titles.",
                "chart_title": "Most IPL Titles",
                "chart_data": []
            }

    except Exception as e:
        print("Stats error:", e)

    # 🔥 FALLBACK LLM (SAFE)
    try:
        if os.getenv("GROQ_API_KEY"):

            res = groq.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": "You are an IPL cricket analyst."},
                    {"role": "user", "content": question}
                ],
                temperature=0
            )

            answer = res.choices[0].message.content

        else:
            answer = "AI service not configured."

    except Exception as e:
        print("LLM Error:", e)
        answer = "Unable to answer right now."

    return {
        "answer": answer,
        "chart_title": "",
        "chart_data": []
    }

# ---------------- PLAYER BATTLE ----------------

@app.get("/player-battle")
def player_battle(p1:str,p2:str):

    load_dataset()

    p1 = resolve_player(p1)
    p2 = resolve_player(p2)

    def build_stats(player):

        runs = runs_cache.get(player,0)
        wickets = wickets_cache.get(player,0)
        sixes = sixes_cache.get(player,0)
        balls = balls_faced_cache.get(player,1)
        dismissals = dismissals_cache.get(player,1)
        fours = fours_cache.get(player,0)
        matches = matches_played_cache.get(player,1)

        strike_rate = round((runs/balls)*100,2) if balls>0 else 0
        average = round((runs/dismissals),2) if dismissals>0 else runs

        return {
            "runs": runs,
            "wickets": wickets,
            "sixes": sixes,
            "fours": fours,
            "balls": balls,
            "matches": matches,
            "strike_rate": strike_rate,
            "average": average
        }

    stats1 = build_stats(p1)
    stats2 = build_stats(p2)

    impact1 = stats1["runs"] + stats1["wickets"]*20 + stats1["sixes"]*2
    impact2 = stats2["runs"] + stats2["wickets"]*20 + stats2["sixes"]*2

    winner = p1 if impact1 > impact2 else p2

    return {
        "player1":p1,
        "player2":p2,
        "stats1":stats1,
        "stats2":stats2,
        "impact1":impact1,
        "impact2":impact2,
        "winner":winner,
        "explanation":{
            "radar":"Compares overall performance across multiple dimensions like runs, wickets and strike rate.",
            "pie":"Shows scoring distribution across field areas (Off, Leg, Straight).",
            "wagon":"Visual direction of shots played by batter.",
            "pitch":"Ball impact zones on pitch showing length distribution."
        }
    }


@app.get("/player-shotmap")
def player_shotmap(player:str):
    return {
        "data":{
            "off": random.randint(10,100),
            "leg": random.randint(10,100),
            "straight": random.randint(10,100)
        }
    }


# ---------------- CORE API ----------------

@app.get("/")
def home():
    return {"message":"SportsFan360 AI running"}

@app.get("/feed")
def feed():
    return get_feed()

@app.get("/teams")
def teams():
    return get_teams()

@app.get("/players")
def players(team:str=None):
    return get_players(team)

@app.get("/matches")
def matches():
    return get_matches()

@app.get("/standings")
def standings():
    return get_standings()

# 🔥 ADD FUNCTION HERE (IMPORTANT POSITION)
def generate_trivia_questions():

    load_dataset()

    try:
        questions = []

        players = list(runs_cache.keys())
        bowlers = list(wickets_cache.keys())

        # 🧠 CATEGORY 1: Runs Leader
        top_run = max(runs_cache, key=runs_cache.get)
        questions.append({
            "question": "Who has scored the most IPL runs?",
            "options": random.sample(players, 3) + [top_run],
            "answer": top_run
        })

        # 🧠 CATEGORY 2: Wickets Leader
        top_wicket = max(wickets_cache, key=wickets_cache.get)
        questions.append({
            "question": "Who has taken the most IPL wickets?",
            "options": random.sample(bowlers, 3) + [top_wicket],
            "answer": top_wicket
        })

        # 🧠 CATEGORY 3: Sixes Leader
        top_sixes = max(sixes_cache, key=sixes_cache.get)
        questions.append({
            "question": "Who has hit the most IPL sixes?",
            "options": random.sample(players, 3) + [top_sixes],
            "answer": top_sixes
        })

        # 🧠 CATEGORY 4: Strike Rate Player
        random_player = random.choice(players)
        questions.append({
            "question": f"Which format is {random_player} best known for?",
            "options": ["Test","ODI","T20","All"],
            "answer": "T20"
        })

        # 🧠 CATEGORY 5: Random Runs Compare
        p1, p2 = random.sample(players, 2)
        better = p1 if runs_cache.get(p1,0) > runs_cache.get(p2,0) else p2

        questions.append({
            "question": f"Who has more IPL runs?",
            "options": [p1, p2],
            "answer": better
        })

        # 🧠 CATEGORY 6: Random Wickets Compare
        b1, b2 = random.sample(bowlers, 2)
        better_bowler = b1 if wickets_cache.get(b1,0) > wickets_cache.get(b2,0) else b2

        questions.append({
            "question": "Who has taken more IPL wickets?",
            "options": [b1, b2],
            "answer": better_bowler
        })

        # 🧠 CATEGORY 7: Highest Score
        questions.append({
            "question": "Who scored the highest individual IPL score?",
            "options": ["Chris Gayle","AB de Villiers","Virat Kohli","David Warner"],
            "answer": "Chris Gayle"
        })

        # 🧠 CATEGORY 8: Team Trivia
        questions.append({
            "question": "Which team has won most IPL titles?",
            "options": ["CSK","MI","RCB","KKR"],
            "answer": "MI"
        })

        # 🧠 CATEGORY 9: True/False Style
        p = random.choice(players)
        questions.append({
            "question": f"{p} is an IPL player.",
            "options": ["True","False"],
            "answer": "True"
        })

        # 🧠 CATEGORY 10: Random Player Exists
        fake_name = "John Cricket"
        questions.append({
            "question": f"Is {fake_name} an IPL player?",
            "options": ["Yes","No"],
            "answer": "No"
        })

        # 🔥 FINAL RANDOMIZE
        for q in questions:
            random.shuffle(q["options"])

        random.shuffle(questions)

        return {
            "questions": questions[:10]
        }

    except Exception as e:
        print("Trivia Error:", e)
        return {"questions": []}


# 🔥 ROUTE (KEEP THIS SAME)
@app.get("/trivia")
def trivia():
    return generate_trivia_questions()


from live_matches import get_live_matches

@app.get("/live-matches")
def live_matches():
    return get_live_matches()
    
    
@app.get("/match-commentary")
def match_commentary(team1:str, team2:str, status:str):

    try:

        # 🔥 BASIC FAKE SCORE (until real API added)
        score_data = {
            "team1": team1,
            "score1": f"{random.randint(80,200)}/{random.randint(1,9)}",
            "team2": team2,
            "score2": f"{random.randint(80,200)}/{random.randint(1,9)}",
            "overs": f"{random.randint(10,20)}.{random.randint(0,5)}"
        }

        prompt = f"""
        You are a professional cricket analyst.

        Match: {team1} vs {team2}
        Status: {status}

        Give a short live match commentary (2-3 lines).
        Make it sharp, realistic, and match situation aware.
        """

        if os.getenv("GROQ_API_KEY"):

            res = groq.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role":"system","content":"You are a cricket expert."},
                    {"role":"user","content":prompt}
                ],
                temperature=0.7
            )

            answer = res.choices[0].message.content

        else:
            answer = f"{team1} vs {team2} is in progress. Momentum shifting with every over."

    except Exception as e:
        print("Commentary Error:", e)
        answer = "Unable to generate commentary."
        score_data = None

    return {
        "score": score_data,
        "commentary": answer
    }
    
    
    
# 🔥 SAFE LOAD
try:
    load_dataset()
except Exception as e:
    print("Startup load failed:", e)