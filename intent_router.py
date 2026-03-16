import re

def detect_intent(q):

    q=q.lower()

    if "run" in q and "most" in q:
        return "runs"

    if "wicket" in q:
        return "wickets"

    if "six" in q:
        return "sixes"

    if "title" in q:
        return "titles"

    if "highest score" in q:
        return "highest"

    if "points table" in q or "standings" in q:
        return "points_table"

    if "live match" in q or "today match" in q:
        return "live_matches"

    return "knowledge"