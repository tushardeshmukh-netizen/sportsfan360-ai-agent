runs_cache={}
wickets_cache={}
titles_cache={}
highest_score_cache={}
sixes_cache={}

<<<<<<< HEAD
def set_caches(runs,wickets,titles,highest,sixes):
    global runs_cache,wickets_cache,titles_cache,highest_score_cache,sixes_cache

    runs_cache=runs
    wickets_cache=wickets
    titles_cache=titles
    highest_score_cache=highest
    sixes_cache=sixes
=======
def set_caches(r,w,t,h,s):
    global runs_cache,wickets_cache,titles_cache,highest_score_cache,sixes_cache
    runs_cache=r
    wickets_cache=w
    titles_cache=t
    highest_score_cache=h
    sixes_cache=s
>>>>>>> agent-v4


def top_runs():

<<<<<<< HEAD
    data=sorted(runs_cache.items(),key=lambda x:x[1],reverse=True)[:10]

    return {
    "chart_title":"Top IPL Run Scorers",
    "chart_data":[{"player":p,"value":v} for p,v in data],
    "answer":f"{data[0][0]} leads IPL run scoring with {data[0][1]} runs."
=======
    top=sorted(runs_cache.items(),key=lambda x:x[1],reverse=True)[:5]

    chart=[{"player":p,"value":v} for p,v in top]

    answer=f"{top[0][0]} has the most IPL runs with {top[0][1]} runs."

    return {
    "chart_title":"Top IPL Run Scorers",
    "chart_data":chart,
    "answer":answer
>>>>>>> agent-v4
    }


def top_wickets():

<<<<<<< HEAD
    data=sorted(wickets_cache.items(),key=lambda x:x[1],reverse=True)[:10]

    return {
    "chart_title":"Top IPL Wicket Takers",
    "chart_data":[{"player":p,"value":v} for p,v in data],
    "answer":f"{data[0][0]} has taken the most IPL wickets."
=======
    top=sorted(wickets_cache.items(),key=lambda x:x[1],reverse=True)[:5]

    chart=[{"player":p,"value":v} for p,v in top]

    answer=f"{top[0][0]} has taken the most IPL wickets with {top[0][1]}."

    return {
    "chart_title":"Top IPL Wicket Takers",
    "chart_data":chart,
    "answer":answer
>>>>>>> agent-v4
    }


def top_sixes():

<<<<<<< HEAD
    data=sorted(sixes_cache.items(),key=lambda x:x[1],reverse=True)[:10]

    return {
    "chart_title":"Most IPL Sixes",
    "chart_data":[{"player":p,"value":v} for p,v in data],
    "answer":f"{data[0][0]} has hit the most sixes in IPL history."
=======
    top=sorted(sixes_cache.items(),key=lambda x:x[1],reverse=True)[:5]

    chart=[{"player":p,"value":v} for p,v in top]

    answer=f"{top[0][0]} has hit the most IPL sixes with {top[0][1]}."

    return {
    "chart_title":"Most IPL Sixes",
    "chart_data":chart,
    "answer":answer
>>>>>>> agent-v4
    }


def team_titles():

<<<<<<< HEAD
    data=sorted(titles_cache.items(),key=lambda x:x[1],reverse=True)

    return {
    "chart_title":"Most IPL Titles",
    "chart_data":[{"player":t,"value":c} for t,c in data],
    "answer":f"{data[0][0]} has won the most IPL titles."
=======
    top=sorted(titles_cache.items(),key=lambda x:x[1],reverse=True)

    chart=[{"player":t,"value":v} for t,v in top]

    answer=f"{top[0][0]} has won the most IPL titles with {top[0][1]} championships."

    return {
    "chart_title":"IPL Titles by Team",
    "chart_data":chart,
    "answer":answer
>>>>>>> agent-v4
    }


def highest_score():

<<<<<<< HEAD
    return {
    "chart_title":"Highest IPL Score",
    "chart_data":[
    {"player":highest_score_cache["player"],"value":highest_score_cache["runs"]}
    ],
    "answer":f"{highest_score_cache['player']} scored {highest_score_cache['runs']} runs in {highest_score_cache['match']}."
=======
    p=highest_score_cache["player"]
    r=highest_score_cache["runs"]
    m=highest_score_cache["match"]

    return {
    "chart_title":"",
    "chart_data":[],
    "answer":f"Highest IPL score is {r} by {p} in {m}."
>>>>>>> agent-v4
    }