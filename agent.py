import requests
import json
import zipfile
import io
import os
import re

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from groq import Groq

from stats_engine import *
from intent_router import detect_intent
from memory_store import save_context,get_context
from knowledge_base import get_player_info

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

    global dataset_loaded
    global runs_cache
    global wickets_cache
    global titles_cache
    global highest_score_cache
    global sixes_cache

    if dataset_loaded:
        return

    r=requests.get(DATA_URL,timeout=120)
    zip_file=zipfile.ZipFile(io.BytesIO(r.content))

    batsman_runs={}
    bowler_wickets={}
    batsman_sixes={}
    highest={"runs":0,"player":None,"match":None}

    for file in zip_file.namelist():

        if not file.endswith(".json"):
            continue

        try:

            match=json.loads(zip_file.read(file))
            info=match.get("info",{})

            teams=info.get("teams",[None,None])
            season=str(info.get("season"))
            winner=info.get("outcome",{}).get("winner")
            date=info.get("dates",[""])[0]

            if season not in season_latest_match:
                season_latest_match[season]={"date":date,"winner":winner}
            else:
                if date>season_latest_match[season]["date"]:
                    season_latest_match[season]={"date":date,"winner":winner}

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

            for p,r in match_runs.items():

                if r>highest["runs"]:
                    highest={
                    "runs":r,
                    "player":p,
                    "match":f"{teams[0]} vs {teams[1]} ({season})"
                    }

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


# ---------------- LLM ----------------

def knowledge_answer(question):

    try:

        res=groq.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
        {"role":"system","content":"You are an IPL cricket analyst. Answer briefly."},
        {"role":"user","content":question}
        ],
        temperature=0
        )

        answer=res.choices[0].message.content

    except:

        answer="Unable to answer."

    return {
    "chart_title":"",
    "chart_data":[],
    "answer":answer
    }


# ---------------- AGENT ----------------

def run_agent(question):

    load_dataset()

    intent=detect_intent(question)

    if intent=="runs":
        return top_runs()

    if intent=="wickets":
        return top_wickets()

    if intent=="titles":
        return team_titles()

    if intent=="highest":
        return highest_score()

    if intent=="sixes":
        return top_sixes()

    return knowledge_answer(question)


@app.get("/")
def home():
    return {"message":"SportsFan360 AI running"}

@app.get("/ask")
def ask(question:str):
    return run_agent(question)
#update 
