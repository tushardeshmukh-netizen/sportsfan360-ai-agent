<<<<<<< HEAD
runs_cache={}
wickets_cache={}
titles_cache={}
highest_score_cache={}
sixes_cache={}

def set_caches(runs,wickets,titles,highest,sixes):
    global runs_cache,wickets_cache,titles_cache,highest_score_cache,sixes_cache

    runs_cache=runs
    wickets_cache=wickets
    titles_cache=titles
    highest_score_cache=highest
    sixes_cache=sixes


def top_runs():

    data=sorted(runs_cache.items(),key=lambda x:x[1],reverse=True)[:10]

    return {
    "chart_title":"Top IPL Run Scorers",
    "chart_data":[{"player":p,"value":v} for p,v in data],
    "answer":f"{data[0][0]} leads IPL run scoring with {data[0][1]} runs."
    }


def top_wickets():

    data=sorted(wickets_cache.items(),key=lambda x:x[1],reverse=True)[:10]

    return {
    "chart_title":"Top IPL Wicket Takers",
    "chart_data":[{"player":p,"value":v} for p,v in data],
    "answer":f"{data[0][0]} has taken the most IPL wickets."
    }


def top_sixes():

    data=sorted(sixes_cache.items(),key=lambda x:x[1],reverse=True)[:10]

    return {
    "chart_title":"Most IPL Sixes",
    "chart_data":[{"player":p,"value":v} for p,v in data],
    "answer":f"{data[0][0]} has hit the most sixes in IPL history."
    }


def team_titles():

    data=sorted(titles_cache.items(),key=lambda x:x[1],reverse=True)

    return {
    "chart_title":"Most IPL Titles",
    "chart_data":[{"player":t,"value":c} for t,c in data],
    "answer":f"{data[0][0]} has won the most IPL titles."
    }


def highest_score():

    return {
    "chart_title":"Highest IPL Score",
    "chart_data":[
    {"player":highest_score_cache["player"],"value":highest_score_cache["runs"]}
    ],
    "answer":f"{highest_score_cache['player']} scored {highest_score_cache['runs']} runs in {highest_score_cache['match']}."
=======
runs_cache={}
wickets_cache={}
titles_cache={}
highest_score_cache={}
sixes_cache={}

def set_caches(runs,wickets,titles,highest,sixes):
    global runs_cache,wickets_cache,titles_cache,highest_score_cache,sixes_cache

    runs_cache=runs
    wickets_cache=wickets
    titles_cache=titles
    highest_score_cache=highest
    sixes_cache=sixes


def top_runs():

    data=sorted(runs_cache.items(),key=lambda x:x[1],reverse=True)[:10]

    return {
    "chart_title":"Top IPL Run Scorers",
    "chart_data":[{"player":p,"value":v} for p,v in data],
    "answer":f"{data[0][0]} leads IPL run scoring with {data[0][1]} runs."
    }


def top_wickets():

    data=sorted(wickets_cache.items(),key=lambda x:x[1],reverse=True)[:10]

    return {
    "chart_title":"Top IPL Wicket Takers",
    "chart_data":[{"player":p,"value":v} for p,v in data],
    "answer":f"{data[0][0]} has taken the most IPL wickets."
    }


def top_sixes():

    data=sorted(sixes_cache.items(),key=lambda x:x[1],reverse=True)[:10]

    return {
    "chart_title":"Most IPL Sixes",
    "chart_data":[{"player":p,"value":v} for p,v in data],
    "answer":f"{data[0][0]} has hit the most sixes in IPL history."
    }


def team_titles():

    data=sorted(titles_cache.items(),key=lambda x:x[1],reverse=True)

    return {
    "chart_title":"Most IPL Titles",
    "chart_data":[{"player":t,"value":c} for t,c in data],
    "answer":f"{data[0][0]} has won the most IPL titles."
    }


def highest_score():

    return {
    "chart_title":"Highest IPL Score",
    "chart_data":[
    {"player":highest_score_cache["player"],"value":highest_score_cache["runs"]}
    ],
    "answer":f"{highest_score_cache['player']} scored {highest_score_cache['runs']} runs in {highest_score_cache['match']}."
>>>>>>> 7a1f20c (UI update)
    }