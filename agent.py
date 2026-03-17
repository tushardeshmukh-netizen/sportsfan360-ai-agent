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


# ---------------- TRIVIA ENGINE ----------------

def random_options(correct,pool):

    pool=list(set(pool)-{correct})

    if len(pool)<3:
        pool=pool+[correct]

    options=random.sample(pool,min(3,len(pool)))
    options.append(correct)

    random.shuffle(options)

    return options


def generate_dataset_trivia():

    questions=[]

    if runs_cache:
        top=max(runs_cache,key=runs_cache.get)
        questions.append({
        "q":"Who has scored the most runs in IPL history?",
        "options":random_options(top,list(runs_cache.keys())),
        "answer":top
        })

    if wickets_cache:
        top=max(wickets_cache,key=wickets_cache.get)
        questions.append({
        "q":"Who has taken the most wickets in IPL history?",
        "options":random_options(top,list(wickets_cache.keys())),
        "answer":top
        })

    if sixes_cache:
        top=max(sixes_cache,key=sixes_cache.get)
        questions.append({
        "q":"Who has hit the most sixes in IPL history?",
        "options":random_options(top,list(sixes_cache.keys())),
        "answer":top
        })

    if titles_cache:
        top=max(titles_cache,key=titles_cache.get)
        questions.append({
        "q":"Which team has won the most IPL titles?",
        "options":random_options(top,list(titles_cache.keys())),
        "answer":top
        })

    if highest_score_cache.get("player"):
        p=highest_score_cache["player"]
        questions.append({
        "q":"Who scored the highest individual IPL score?",
        "options":random_options(p,list(runs_cache.keys())),
        "answer":p
        })

    return questions


def generate_points_table_trivia():

    questions=[]

    try:
        table=get_ipl_points_table()

        if table:
            teams=[t["team"] for t in table]
            leader=table[0]["team"]

            questions.append({
            "q":"Which team is currently leading the IPL points table?",
            "options":random_options(leader,teams),
            "answer":leader
            })

    except:
        pass

    return questions


def generate_dynamic_trivia():

    questions=[]

    players=list(runs_cache.keys())
    teams=list(titles_cache.keys())

    if players:
        p=random.choice(players)
        questions.append({
        "q":"Which of these players is an IPL player?",
        "options":random_options(p,players),
        "answer":p
        })

    if teams:
        t=random.choice(teams)
        questions.append({
        "q":"Which of these is an IPL team?",
        "options":random_options(t,teams),
        "answer":t
        })

    return questions


def generate_trivia_questions():

    load_dataset()

    questions=[]
    questions+=generate_dataset_trivia()
    questions+=generate_points_table_trivia()
    questions+=generate_dynamic_trivia()

    if len(questions)==0:
        return {"questions":[]}

    base=list(questions)

    while len(questions)<10:
        questions.append(random.choice(base))

    random.shuffle(questions)

    return {"questions":questions[:10]}


# ---------------- LLM ANSWER ----------------

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


# ---------------- TRIVIA API ----------------

@app.get("/trivia")
def trivia():
    return generate_trivia_questions()