import random

def get_feed():

    trending_questions=[
        "Most IPL runs",
        "Most IPL wickets",
        "Most IPL sixes",
        "Which team has most IPL titles",
        "Highest IPL score",
        "Compare Kohli vs Rohit",
        "Why is IPL popular"
    ]

    insights=[
        "Teams with strong death bowling often win close IPL matches.",
        "Powerplay strike rate strongly impacts win probability.",
        "Successful IPL teams usually have strong all-rounders.",
        "Teams defending totals win slightly more night matches."
    ]

    stats=[
        "Chris Gayle scored the highest IPL score: 175*.",
        "Virat Kohli holds the record for most IPL runs.",
        "Mumbai Indians have dominated IPL titles historically.",
        "Death over specialists often decide IPL finals."
    ]

    cards=[

        {
            "title":"Trending Question",
            "text":random.choice(trending_questions),
            "type":"question"
        },

        {
            "title":"AI Insight",
            "text":random.choice(insights),
            "type":"insight"
        },

        {
            "title":"Stat Highlight",
            "text":random.choice(stats),
            "type":"stat"
        }

    ]

    return {
        "cards":cards,
        "trending":trending_questions
    }