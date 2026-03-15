import requests
import json
import zipfile
import io
import os
import re
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from groq import Groq

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
player_index={}

def load_dataset():

    global dataset_loaded,runs_cache,wickets_cache,titles_cache,highest_score_cache

    if dataset_loaded:
        return

    r=requests.get(DATA_URL,timeout=120)
    zip_file=zipfile.ZipFile(io.BytesIO(r.content))

    batsman_runs={}
    bowler_wickets={}
    titles={}
    highest={"runs":0,"player":None,"match":None}

    for file in zip_file.namelist():

        if not file.endswith(".json"):
            continue

        try:

            match=json.loads(zip_file.read(file))
            info=match.get("info",{})

            teams=info.get("teams",[None,None])
            season=info.get("season")
            winner=info.get("outcome",{}).get("winner")

            event=info.get("event",{})
            match_number=str(event.get("match_number","")).lower()

            if "final" in match_number and winner:
                titles[winner]=titles.get(winner,0)+1

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

                            for p in batter.lower().split():
                                player_index.setdefault(p,set()).add(batter)

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

    runs_cache=batsman_runs
    wickets_cache=bowler_wickets
    titles_cache=titles
    highest_score_cache=highest

    dataset_loaded=True


# ---------- TOOLS ----------

def get_top_runs():

    data=sorted(runs_cache.items(),key=lambda x:x[1],reverse=True)[:10]

    return {
    "chart_title":"Top IPL Run Scorers",
    "chart_data":[{"player":p,"value":v} for p,v in data],
    "answer":f"{data[0][0]} leads IPL run scoring."
    }


def get_top_wickets():

    data=sorted(wickets_cache.items(),key=lambda x:x[1],reverse=True)[:10]

    return {
    "chart_title":"Top IPL Wicket Takers",
    "chart_data":[{"player":p,"value":v} for p,v in data],
    "answer":f"{data[0][0]} has taken the most IPL wickets."
    }


def get_team_titles():

    if not titles_cache:
        return {
        "chart_title":"Most IPL Titles",
        "chart_data":[],
        "answer":"IPL title data loading. Please try again."
        }

    data=sorted(titles_cache.items(),key=lambda x:x[1],reverse=True)

    return {
    "chart_title":"Most IPL Titles",
    "chart_data":[{"player":t,"value":c} for t,c in data],
    "answer":f"{data[0][0]} has won the most IPL titles."
    }


def get_highest_score():

    return {
    "chart_title":"Highest IPL Score",
    "chart_data":[
    {"player":highest_score_cache["player"],"value":highest_score_cache["runs"]}
    ],
    "answer":f"{highest_score_cache['player']} scored {highest_score_cache['runs']} runs in {highest_score_cache['match']}."
    }


def detect_players(question):

    tokens=re.findall(r"[a-z]+",question.lower())

    found=set()

    for t in tokens:
        if t in player_index:
            found.update(player_index[t])

    return list(found)


def compare_players(players):

    p1,p2=players[:2]

    r1=runs_cache.get(p1,0)
    r2=runs_cache.get(p2,0)

    leader=p1 if r1>r2 else p2

    return {
    "chart_title":f"{p1} vs {p2} IPL Runs",
    "chart_data":[
    {"player":p1,"value":r1},
    {"player":p2,"value":r2}
    ],
    "answer":f"{leader} has scored more IPL runs."
    }


# ---------- TOOL ROUTER ----------

def choose_tool(question):

    try:

        res=groq.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{
        "role":"user",
        "content":f"""
Choose best tool.

TOOLS:
top_runs
top_wickets
team_titles
highest_score
compare_players
knowledge

Return JSON:
{{"tool":"tool_name"}}

Question: {question}
"""
        }],
        temperature=0
        )

        text=res.choices[0].message.content.strip()

        data=json.loads(text)

        return data.get("tool","knowledge")

    except:

        q=question.lower()

        if "title" in q:
            return "team_titles"

        if "wicket" in q:
            return "top_wickets"

        if "run" in q:
            return "top_runs"

        return "knowledge"


# ---------- LLM FALLBACK ----------

def knowledge_answer(question):

    try:

        res=groq.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
        {"role":"system","content":"You are an IPL cricket expert."},
        {"role":"user","content":question}
        ],
        temperature=0.3
        )

        answer=res.choices[0].message.content

    except:

        answer="IPL is popular because it combines world-class players, fast T20 matches, intense rivalries, and massive fan engagement."

    return {
    "chart_title":"",
    "chart_data":[],
    "answer":answer
    }


# ---------- AGENT ----------

def run_agent(question):

    load_dataset()

    tool=choose_tool(question)

    players=detect_players(question)

    if tool=="top_runs":
        return get_top_runs()

    if tool=="top_wickets":
        return get_top_wickets()

    if tool=="team_titles":
        return get_team_titles()

    if tool=="highest_score":
        return get_highest_score()

    if tool=="compare_players" and len(players)>=2:
        return compare_players(players)

    return knowledge_answer(question)


@app.get("/")
def home():
    return {"message":"SportsFan360 AI running"}


@app.get("/ask")
def ask(question:str):
    return run_agent(question)
