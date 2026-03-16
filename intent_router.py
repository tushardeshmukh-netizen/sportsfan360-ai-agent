<<<<<<< HEAD
def detect_intent(question):

    q=question.lower()

    if "six" in q:
        return "sixes"
=======
import re

def detect_intent(q):

    q=q.lower()

    if "run" in q and "most" in q:
        return "runs"
>>>>>>> agent-v4

    if "wicket" in q:
        return "wickets"

<<<<<<< HEAD
    if "run" in q:
        return "runs"
=======
    if "six" in q:
        return "sixes"
>>>>>>> agent-v4

    if "title" in q:
        return "titles"

<<<<<<< HEAD
    if "highest" in q:
        return "highest"

    if "compare" in q:
        return "compare"
=======
    if "highest score" in q:
        return "highest"

    if "points table" in q or "standings" in q:
        return "points_table"

    if "live match" in q or "today match" in q:
        return "live_matches"
>>>>>>> agent-v4

    return "knowledge"