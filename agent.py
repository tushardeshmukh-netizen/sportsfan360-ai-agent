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
def generate_trivia_questions():

    load_dataset()
    import random
    import re

    def is_valid_player(name):
        if not isinstance(name,str):
            return False
        name=name.strip()
        if re.match(r'^[a-f0-9]{6,}$', name.lower()):
            return False
        if len(name)<4:
            return False
        if " " not in name:
            return False
        return True

    players=[p for p in all_players if is_valid_player(p)]

    if len(players)<20:
        return {"error":"Not enough players"}

    questions=[]

    runs_sorted=sorted(runs_cache.items(), key=lambda x:x[1], reverse=True)
    wickets_sorted=sorted(wickets_cache.items(), key=lambda x:x[1], reverse=True)
    sixes_sorted=sorted(sixes_cache.items(), key=lambda x:x[1], reverse=True)

    def wrong(correct):
        opts=[]
        while len(opts)<3:
            p=random.choice(players)
            if p!=correct and p not in opts:
                opts.append(p)
        return opts

    def make(q, correct):
        options=wrong(correct)+[correct]
        random.shuffle(options)
        return {"q":q,"options":options,"answer":correct}

    for _ in range(10):

        # 🔥 RANDOMLY PICK DATA SOURCE (NOT CATEGORY NAME)
        choice=random.randint(1,8)

        # 1️⃣ TOP PLAYER
        if choice==1 and runs_sorted:
            p=random.choice(runs_sorted[:10])[0]
            questions.append(make("Which player is among IPL's top performers?",p))

        # 2️⃣ HIGH IMPACT PLAYER
        elif choice==2 and wickets_sorted:
            p=random.choice(wickets_sorted[:10])[0]
            questions.append(make("Which player has had major impact with the ball in IPL?",p))

        # 3️⃣ POWER HITTER
        elif choice==3 and sixes_sorted:
            p=random.choice(sixes_sorted[:15])[0]
            questions.append(make("Who is known as a powerful hitter in IPL?",p))

        # 4️⃣ RANDOM PERFORMANCE BAND
        elif choice==4 and runs_sorted:
            p,v=random.choice(runs_sorted[10:60])
            if is_valid_player(p):
                questions.append(make(f"Which player has around {v} runs in IPL?",p))

        # 5️⃣ LOW PROFILE PLAYER
        elif choice==5 and runs_sorted:
            p=random.choice(runs_sorted[50:120])[0]
            if is_valid_player(p):
                questions.append(make("Which player has quietly contributed in IPL?",p))

        # 6️⃣ COMPARISON
        elif choice==6 and len(runs_sorted)>20:
            p1=random.choice(runs_sorted[:30])[0]
            p2=random.choice(runs_sorted[:30])[0]

            if p1!=p2 and is_valid_player(p1) and is_valid_player(p2):
                correct = p1 if runs_cache[p1]>runs_cache[p2] else p2

                options=[p1,p2]
                while len(options)<4:
                    x=random.choice(players)
                    if x not in options:
                        options.append(x)

                random.shuffle(options)

                questions.append({
                    "q":"Who has scored more IPL runs?",
                    "options":options,
                    "answer":correct
                })

        # 7️⃣ RANDOM PLAYER PRESENCE
        elif choice==7:
            p=random.choice(players)
            questions.append(make("Which of these players has played in IPL?",p))

        # 8️⃣ MIXED STAT LOGIC
        elif choice==8:
            p=random.choice(players)
            questions.append(make("Identify a known IPL cricketer.",p))

   # 🔥 REMOVE DUPLICATE QUESTIONS (same text)
unique_questions=[]
seen=set()

for q in questions:
    if q["q"] not in seen:
        unique_questions.append(q)
        seen.add(q["q"])

# 🔥 ENSURE 10 QUESTIONS
while len(unique_questions)<10:
    p=random.choice(players)
    options=random.sample(players,3)
    if p not in options:
        options[0]=p
    random.shuffle(options)

    unique_questions.append({
        "q":"Identify the IPL player.",
        "options":options,
        "answer":p
    })

random.shuffle(unique_questions)

return unique_questions[:10]

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