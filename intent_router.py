def detect_intent(question):

    q=question.lower()

    if "six" in q:
        return "sixes"

    if "wicket" in q:
        return "wickets"

    if "run" in q:
        return "runs"

    if "title" in q:
        return "titles"

    if "highest" in q:
        return "highest"

    if "compare" in q:
        return "compare"

    return "knowledge"