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


DATA_URL="https://cricsheet.org/downloads/ipl_json.zip"

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

# 🔥 HUMAN FRIENDLY NAMES (IMPORTANT FIX)
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

        # map full
        name_map[clean]=p

        # map last name
        if len(parts)>=2:
            name_map[parts[-1]]=p

        # map initials (V Kohli → virat kohli)
        if len(parts)>=2:
            name_map[parts[0]+" "+parts[-1]]=p


def resolve_player(name):

    # 🔥 direct alias mapping
    if name in player_alias:
        return player_alias[name]

    # 🔥 reverse alias
    for full, short in player_alias.items():
        if name == short:
            return short

    # 🔥 exact match
    if name in runs_cache:
        return name

    key=name.lower().replace(".", "").strip()

    if key in name_map:
        return name_map[key]

    # 🔥 fallback fuzzy
    for p in runs_cache.keys():
        if key in p.lower():
            return p

    return name


# ---------------- DATASET LOADER ----------------

def load_dataset():

    global dataset_loaded,runs_cache,wickets_cache,titles_cache
    global highest_score_cache,sixes_cache,season_latest_match
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

    titles={}
    for season,data in season_latest_match.items():
        winner=data["winner"]
        if winner:
            titles[winner]=titles.get(winner,0)+1

    runs_cache=batsman_runs
    wickets_cache=bowler_wickets
    titles_cache=titles
    highest_score_cache=highest
    sixes_cache=batsman_sixes

    balls_faced_cache=balls_faced
    dismissals_cache=dismissals
    fours_cache=fours
    matches_played_cache=matches_played

    set_caches(runs_cache,wickets_cache,titles_cache,highest_score_cache,sixes_cache)

    # 🔥 BUILD NAME MAP HERE
    build_name_map()

    dataset_loaded=True
    print("Dataset Loaded")


# ---------------- TRIVIA ENGINE ----------------

def generate_trivia_questions():
    load_dataset()
    questions=[]
    used=set()

    players=list(runs_cache.keys())

    if len(players)<50:
        return {"questions":[]}

    while len(questions)<10:
        try:
            opts=random.sample(players,4)
            correct=max(opts,key=lambda x:runs_cache[x])

            q={
                "q":"Who has scored the most IPL runs among these?",
                "options":opts,
                "answer":correct
            }

            key=q["q"]+str(q["options"])
            if key in used:
                continue

            used.add(key)
            questions.append(q)

        except:
            continue

    return {"questions":questions}


# ---------------- PLAYER APIs ----------------

@app.get("/player-list")
def player_list():
    load_dataset()

    # dataset players
    base_players = set(all_players)

    # 🔥 ADD FULL NAMES
    for full, short in player_alias.items():
        base_players.add(full)

    # 🔥 RETURN CLEAN SORTED LIST
    return {
        "players": sorted(list(base_players))
    }
    
    
@app.get("/player-battle")
def player_battle(p1:str,p2:str):

    load_dataset()

    # 🔥 FIX NAME HERE
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
        "winner":winner
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


# ---------------- LLM ----------------

def knowledge_answer(question):

    try:
        res=groq.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
        {"role":"system","content":"You are an IPL cricket analyst."},
        {"role":"user","content":question}
        ],
        temperature=0
        )
        answer=res.choices[0].message.content
    except:
        answer="Unable to answer."

    return {"answer":answer}


# ---------------- AGENT ----------------

def run_agent(question):

    load_dataset()
    intent=detect_intent(question)

    if intent=="runs":
        result=top_runs()
    elif intent=="wickets":
        result=top_wickets()
    elif intent=="titles":
        result=team_titles()
    elif intent=="highest":
        result=highest_score()
    elif intent=="sixes":
        result=top_sixes()
    else:
        result=knowledge_answer(question)

    save_context(question,result["answer"])
    return result


# ---------------- API ----------------

@app.get("/")
def home():
    return {"message":"SportsFan360 AI running"}

@app.get("/ask")
def ask(question:str):
    return run_agent(question)

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

@app.get("/trivia")
def trivia():
    return generate_trivia_questions()


# 🔥 LOAD DATA ON START
load_dataset()