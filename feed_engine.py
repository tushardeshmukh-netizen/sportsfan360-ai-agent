import random

def get_feed():

    trending=[
        "Most IPL runs",
        "Most IPL wickets",
        "Most IPL sixes",
        "Which team has most IPL titles",
        "Highest IPL score"
    ]

    insights=[
        "Teams with strong death bowling often win close IPL matches.",
        "Powerplay strike rate strongly impacts win probability.",
        "Successful IPL teams usually have strong all-rounders.",
        "Teams defending totals win slightly more night games."
    ]

    stats=[
        "Chris Gayle holds the highest IPL score: 175*.",
        "Virat Kohli is the all-time leading IPL run scorer.",
        "Mumbai Indians are among the most successful IPL teams.",
        "Death overs often decide close IPL matches."
    ]

    cards=[

        {
            "title":"Trending Question",
            "text":random.choice(trending),
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
        "trending":trending
    }