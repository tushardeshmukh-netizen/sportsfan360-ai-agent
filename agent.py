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

    load_dataset()

    questions=[]
    players=list(all_players)

    if len(players)<10:
        return {"error":"Not enough data"}

    # ---- BUILD DATA POOLS ----
    runs_sorted=sorted(runs_cache.items(), key=lambda x:x[1], reverse=True)
    wickets_sorted=sorted(wickets_cache.items(), key=lambda x:x[1], reverse=True)
    sixes_sorted=sorted(sixes_cache.items(), key=lambda x:x[1], reverse=True)

    def generate_wrong_answers(correct, pool):
        wrong=[]
        attempts=0

        while len(wrong)<3 and attempts<20:
            p=random.choice(pool)
            if p!=correct and p not in wrong:
                wrong.append(p)
            attempts+=1

        return wrong

    def create_question_from_stat(stat_list, label):

        if len(stat_list)<5:
            return None

        # pick random index → NOT always top
        idx=random.randint(0, min(30,len(stat_list)-1))

        player,value=stat_list[idx]

        # dynamic question
        q=f"Which player has around {value} {label} in IPL?"

        wrong=generate_wrong_answers(player, players)

        options=wrong+[player]
        random.shuffle(options)

        return {
            "q": q,
            "options": options,
            "answer": player
        }

    # ---- GENERATE QUESTIONS ----

    q1=create_question_from_stat(runs_sorted, "runs")
    q2=create_question_from_stat(wickets_sorted, "wickets")
    q3=create_question_from_stat(sixes_sorted, "sixes")

    if q1: questions.append(q1)
    if q2: questions.append(q2)
    if q3: questions.append(q3)

    # ---- PLAYER COMPARISON (SMART) ----
    if len(runs_sorted)>10:
        p1=random.choice(runs_sorted[:20])[0]
        p2=random.choice(runs_sorted[:20])[0]

        if p1!=p2:
            correct = p1 if runs_cache[p1]>runs_cache[p2] else p2

            options=[p1,p2]
            while len(options)<4:
                x=random.choice(players)
                if x not in options:
                    options.append(x)

            random.shuffle(options)

            questions.append({
                "q": f"Who has scored more IPL runs?",
                "options": options,
                "answer": correct
            })

    # ---- PURE DATA-DRIVEN RANDOM FACT ----
    for _ in range(6):

        stat_type=random.choice(["runs","wickets","sixes"])

        if stat_type=="runs" and runs_sorted:
            stat_list=runs_sorted
            label="runs"
        elif stat_type=="wickets" and wickets_sorted:
            stat_list=wickets_sorted
            label="wickets"
        else:
            stat_list=sixes_sorted
            label="sixes"

        q=create_question_from_stat(stat_list,label)

        if q:
            questions.append(q)

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