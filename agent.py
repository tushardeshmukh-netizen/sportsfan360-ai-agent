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

# ---------------- DATASET LOADER ----------------

def load_dataset():

    global dataset_loaded,runs_cache,wickets_cache,titles_cache
    global highest_score_cache,sixes_cache,season_latest_match

    if dataset_loaded:
        return

    print("Loading IPL dataset...")

    r=requests.get(DATA_URL,timeout=120)
    zip_file=zipfile.ZipFile(io.BytesIO(r.content))

    batsman_runs={}
    bowler_wickets={}
    batsman_sixes={}
    highest={"runs":0,"player":None}

    for file in zip_file.namelist():

        if not file.endswith(".json"):
            continue

        try:
            match=json.loads(zip_file.read(file))

            match_runs={}

            for inn in match.get("innings",[]):
                for over in inn.get("overs",[]):
                    for d in over.get("deliveries",[]):

                        batter=d.get("batter")
                        bowler=d.get("bowler")
                        runs=d.get("runs",{}).get("batter",0)

                        if batter:
                            batsman_runs[batter]=batsman_runs.get(batter,0)+runs
                            match_runs[batter]=match_runs.get(batter,0)+runs

                            if runs==6:
                                batsman_sixes[batter]=batsman_sixes.get(batter,0)+1

                        wickets=d.get("wickets",[])
                        if wickets and bowler:
                            bowler_wickets[bowler]=bowler_wickets.get(bowler,0)+len(wickets)

            for p,runs in match_runs.items():
                if runs>highest["runs"]:
                    highest={"runs":runs,"player":p}

        except:
            continue

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

    set_caches(runs_cache,wickets_cache,titles_cache,highest_score_cache,sixes_cache)

    dataset_loaded=True
    print("Dataset Loaded")


# ---------------- TRIVIA ENGINE (FIXED) ----------------

def generate_trivia_questions():

    load_dataset()

    questions=[]
    used=set()

    players=list(runs_cache.keys())
    bowlers=list(wickets_cache.keys())
    teams=list(titles_cache.keys())

    if len(players)<50:
        return {"questions":[]}

    attempts=0

    while len(questions)<10 and attempts<100:

        attempts+=1

        q_type=random.choice([
            "runs_compare",
            "wickets_compare",
            "titles_compare",
            "top_player",
            "lowest_player",
            "top_bowler",
            "odd_one_out",
            "milestone_runs",
            "closest_runs",
            "multi_best",
            "player_identify",
            "team_identify"
        ])

        try:

            if q_type=="runs_compare":
                p1,p2=random.sample(players,2)
                correct=max([p1,p2],key=lambda x:runs_cache[x])
                options=[p1,p2] + random.sample(players,2)

                q={
                "q":"Who has scored more IPL runs?",
                "options":list(set(options))[:4],
                "answer":correct
                }

            elif q_type=="wickets_compare":
                p1,p2=random.sample(bowlers,2)
                correct=max([p1,p2],key=lambda x:wickets_cache[x])
                options=[p1,p2] + random.sample(bowlers,2)

                q={
                "q":"Who has taken more IPL wickets?",
                "options":list(set(options))[:4],
                "answer":correct
                }

            elif q_type=="titles_compare":
                if len(teams)<2:
                    continue
                t1,t2=random.sample(teams,2)
                correct=max([t1,t2],key=lambda x:titles_cache.get(x,0))
                options=[t1,t2] + random.sample(teams,2)

                q={
                "q":"Which team has more IPL titles?",
                "options":list(set(options))[:4],
                "answer":correct
                }

            elif q_type=="top_player":
                opts=random.sample(players,4)
                correct=max(opts,key=lambda x:runs_cache[x])

                q={"q":"Who scored the most IPL runs?","options":opts,"answer":correct}

            elif q_type=="lowest_player":
                opts=random.sample(players,4)
                correct=min(opts,key=lambda x:runs_cache[x])

                q={"q":"Who scored the least IPL runs?","options":opts,"answer":correct}

            elif q_type=="top_bowler":
                opts=random.sample(bowlers,4)
                correct=max(opts,key=lambda x:wickets_cache[x])

                q={"q":"Who has most IPL wickets?","options":opts,"answer":correct}

            elif q_type=="odd_one_out":
                opts=random.sample(players,4)
                correct=min(opts,key=lambda x:runs_cache[x])

                q={"q":"Find lowest run scorer","options":opts,"answer":correct}

            elif q_type=="milestone_runs":
                p=random.choice(players)
                runs=runs_cache[p]
                milestone=1000*(runs//1000)

                options=[
                    f"{milestone}+",
                    f"{milestone+1000}+",
                    f"{max(0,milestone-1000)}+",
                    f"{milestone+500}+"
                ]

                q={
                "q":f"{p} falls into which run bracket?",
                "options":options,
                "answer":f"{milestone}+"
                }

            elif q_type=="closest_runs":
                target=random.randint(1000,6000)
                opts=random.sample(players,4)
                correct=min(opts,key=lambda x:abs(runs_cache[x]-target))

                q={
                "q":f"Who is closest to {target} runs?",
                "options":opts,
                "answer":correct
                }

            elif q_type=="multi_best":
                opts=random.sample(players,4)
                correct=max(opts,key=lambda x:runs_cache[x])

                q={"q":"Highest run scorer?","options":opts,"answer":correct}

            elif q_type=="player_identify":
                real=random.choice(players)
                fake=f"Player_{random.randint(1000,9999)}"
                fake2=f"Player_{random.randint(1000,9999)}"
                fake3=f"Player_{random.randint(1000,9999)}"

                opts=[real,fake,fake2,fake3]
                random.shuffle(opts)

                q={"q":"Which is real IPL player?","options":opts,"answer":real}

            elif q_type=="team_identify":
                if not teams:
                    continue
                real=random.choice(teams)
                opts=[real,f"Team_{random.randint(100,999)}",f"Team_{random.randint(100,999)}",f"Team_{random.randint(100,999)}"]
                random.shuffle(opts)

                q={"q":"Which is IPL team?","options":opts,"answer":real}

            key=q["q"]+str(q["answer"])

            if key in used:
                continue

            used.add(key)
            questions.append(q)

        except:
            continue

    return {"questions":questions}


# ---------------- REST UNCHANGED ----------------

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