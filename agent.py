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

all_players=set()

# 🔥 NEW
shotmap_cache={}
pitchmap_cache={}


# ---------------- DATASET LOADER ----------------

def load_dataset():

    global dataset_loaded,runs_cache,wickets_cache,titles_cache
    global highest_score_cache,sixes_cache,season_latest_match,all_players
    global shotmap_cache,pitchmap_cache

    if dataset_loaded:
        return

    print("Loading IPL dataset...")

    try:
        r=requests.get(DATA_URL,timeout=120)
        zip_file=zipfile.ZipFile(io.BytesIO(r.content))
    except Exception as e:
        print("DATA LOAD FAILED:",e)
        return

    batsman_runs={}
    bowler_wickets={}
    batsman_sixes={}
    highest={"runs":0,"player":None}

    players_set=set()

    for file in zip_file.namelist():

        if not file.endswith(".json"):
            continue

        try:
            match=json.loads(zip_file.read(file))

            match_runs={}

            info=match.get("info",{})
            registry=info.get("registry",{}).get("people",{})
            for name in registry.values():
                if isinstance(name,str):
                    players_set.add(name)

            for inn in match.get("innings",[]):
                for over in inn.get("overs",[]):
                    for d in over.get("deliveries",[]):

                        batter=d.get("batter")
                        bowler=d.get("bowler")
                        runs=d.get("runs",{}).get("batter",0)

                        if batter:
                            players_set.add(batter)
                        if bowler:
                            players_set.add(bowler)

                        if batter:
                            batsman_runs[batter]=batsman_runs.get(batter,0)+runs
                            match_runs[batter]=match_runs.get(batter,0)+runs

                            if runs==6:
                                batsman_sixes[batter]=batsman_sixes.get(batter,0)+1

                            if batter not in shotmap_cache:
                                shotmap_cache[batter]={"off":0,"leg":0,"straight":0}

                            if runs>=6:
                                shotmap_cache[batter]["leg"]+=runs*1.2
                                shotmap_cache[batter]["off"]+=runs*0.8
                            elif runs==4:
                                shotmap_cache[batter]["off"]+=runs*1.3
                                shotmap_cache[batter]["straight"]+=runs*0.5
                            elif runs>=2:
                                shotmap_cache[batter]["straight"]+=runs
                                shotmap_cache[batter]["leg"]+=runs*0.5
                            else:
                                shotmap_cache[batter]["straight"]+=1

                            if batter not in pitchmap_cache:
                                pitchmap_cache[batter]={"full":0,"good":0,"short":0,"wickets":0}

                            if runs>=4:
                                pitchmap_cache[batter]["full"]+=1
                            elif runs==0:
                                pitchmap_cache[batter]["good"]+=1
                            else:
                                pitchmap_cache[batter]["short"]+=1

                        wickets=d.get("wickets",[])
                        if wickets and bowler:
                            bowler_wickets[bowler]=bowler_wickets.get(bowler,0)+len(wickets)

                            for w in wickets:
                                out=w.get("player_out")
                                if out:
                                    players_set.add(out)
                                    pitchmap_cache.setdefault(out,{"full":0,"good":0,"short":0,"wickets":0})
                                    pitchmap_cache[out]["wickets"]+=1

            for p,runs in match_runs.items():
                if runs>highest["runs"]:
                    highest={"runs":runs,"player":p}

        except:
            continue

    all_players=set([p.strip() for p in players_set if isinstance(p,str) and len(p)>2])

    titles={}
    for season,data in season_latest_match.items():
        winner=data.get("winner")
        if winner:
            titles[winner]=titles.get(winner,0)+1

    runs_cache=batsman_runs
    wickets_cache=bowler_wickets
    titles_cache=titles
    highest_score_cache=highest
    sixes_cache=batsman_sixes

    try:
        set_caches(runs_cache,wickets_cache,titles_cache,highest_score_cache,sixes_cache)
    except:
        pass

    dataset_loaded=True
    print(f"Dataset Loaded: {len(all_players)} players")


# ---------------- PLAYER BATTLE ----------------

def get_player_stats(player):
    return {
        "runs": runs_cache.get(player,0),
        "wickets": wickets_cache.get(player,0),
        "sixes": sixes_cache.get(player,0)
    }

def calculate_impact(stats):
    return stats["runs"] + (stats["wickets"] * 20) + (stats["sixes"] * 2)

def compare_players(p1,p2):

    stats1=get_player_stats(p1)
    stats2=get_player_stats(p2)

    impact1=calculate_impact(stats1)
    impact2=calculate_impact(stats2)

    comparison={
        "runs": p1 if stats1["runs"]>stats2["runs"] else p2,
        "wickets": p1 if stats1["wickets"]>stats2["wickets"] else p2,
        "sixes": p1 if stats1["sixes"]>stats2["sixes"] else p2,
        "impact": p1 if impact1>impact2 else p2
    }

    score1=sum(1 for v in comparison.values() if v==p1)
    score2=sum(1 for v in comparison.values() if v==p2)

    winner = p1 if score1>score2 else p2

    return {
        "player1": p1,
        "player2": p2,
        "stats1": stats1,
        "stats2": stats2,
        "impact1": impact1,
        "impact2": impact2,
        "comparison": comparison,
        "score": {p1:score1,p2:score2},
        "winner": winner
    }


# ---------------- APIs ----------------

# ---------------- DYNAMIC TRIVIA ENGINE ----------------

# ---------------- DYNAMIC TRIVIA ENGINE (FIXED NO REPEAT) ----------------

def generate_trivia_questions():

    questions=[]

    players=list(all_players)

    if not players or len(players)<20:
        players=[
            "Virat Kohli","MS Dhoni","Rohit Sharma","Chris Gayle",
            "AB de Villiers","KL Rahul","Jasprit Bumrah","Yuzvendra Chahal",
            "Hardik Pandya","Andre Russell","Ravindra Jadeja","David Warner",
            "Suresh Raina","Shikhar Dhawan","Sunil Narine","Glenn Maxwell",
            "Kieron Pollard","Faf du Plessis","Dinesh Karthik","Ruturaj Gaikwad"
        ]

    random.shuffle(players)

    # ---- SORTED POOLS ----
    top_runs=sorted(runs_cache.items(), key=lambda x:x[1], reverse=True)[:20]
    mid_runs=sorted(runs_cache.items(), key=lambda x:x[1], reverse=True)[20:60]

    top_wickets=sorted(wickets_cache.items(), key=lambda x:x[1], reverse=True)[:20]
    top_sixes=sorted(sixes_cache.items(), key=lambda x:x[1], reverse=True)[:20]

    def get_options(correct, pool):
        opts=set([correct])
        while len(opts)<4:
            opts.add(random.choice(pool))
        opts=list(opts)
        random.shuffle(opts)
        return opts

    # ---------------- QUESTION TYPES ----------------

    # 1 RANDOM TOP RUNNER (not always #1)
    if top_runs:
        correct=random.choice(top_runs[:10])[0]
        options=get_options(correct, players)
        questions.append({
            "q":"Which player is among the top IPL run scorers?",
            "options":options,
            "answer":correct
        })

    # 2 MID PLAYER QUESTION
    if mid_runs:
        correct=random.choice(mid_runs)[0]
        options=get_options(correct, players)
        questions.append({
            "q":"Which of these players has a moderate IPL run record?",
            "options":options,
            "answer":correct
        })

    # 3 TOP WICKET (random from top, not fixed)
    if top_wickets:
        correct=random.choice(top_wickets[:10])[0]
        options=get_options(correct, players)
        questions.append({
            "q":"Which player is known for taking many IPL wickets?",
            "options":options,
            "answer":correct
        })

    # 4 SIXES POWER HITTER
    if top_sixes:
        correct=random.choice(top_sixes[:10])[0]
        options=get_options(correct, players)
        questions.append({
            "q":"Who is a known power hitter in IPL?",
            "options":options,
            "answer":correct
        })

    # 5 HIGHEST SCORE MATCH
    if highest_score_cache.get("player"):
        correct=highest_score_cache["player"]
        options=get_options(correct, players)
        questions.append({
            "q":"Who holds one of the highest individual scores in IPL matches?",
            "options":options,
            "answer":correct
        })

    # 6–10 PURE RANDOMIZED CONTEXT QUESTIONS
    question_templates=[
        "Which of these players has played in the IPL?",
        "Identify a known IPL player.",
        "Which name belongs to an IPL cricketer?",
        "Who among these is part of IPL history?",
        "Pick the correct IPL player."
    ]

    for i in range(5):
        correct=random.choice(players)
        options=get_options(correct, players)

        questions.append({
            "q":random.choice(question_templates),
            "options":options,
            "answer":correct
        })

    # FINAL SHUFFLE (VERY IMPORTANT)
    random.shuffle(questions)

    return questions[:10]


@app.get("/trivia")
def get_trivia():
    return {
        "questions": generate_trivia_questions()
    }
    


@app.get("/")
def home():
    return {"message":"API running"}

@app.get("/player-battle")
def player_battle(p1:str,p2:str):
    load_dataset()
    if not p1 or not p2:
        return {"error":"Missing players"}
    return compare_players(p1,p2)

@app.get("/player-list")
def player_list():
    load_dataset()
    return {"players":sorted(list(all_players))}

@app.get("/player-shotmap")
def player_shotmap(player:str):
    load_dataset()
    return {"data":shotmap_cache.get(player,{"off":0,"leg":0,"straight":0})}

@app.get("/player-pitchmap")
def player_pitchmap(player:str):
    load_dataset()
    return {"data":pitchmap_cache.get(player,{"full":0,"good":0,"short":0,"wickets":0})}