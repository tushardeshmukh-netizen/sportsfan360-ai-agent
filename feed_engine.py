import random
import requests

CRIC_API="https://api.cricapi.com/v1/cricScore"


TRENDING_QUESTIONS=[

"Highest IPL score",
"Most IPL runs",
"Most IPL wickets",
"Which team has most IPL titles",
"Most IPL sixes",
"Fastest IPL century",
"Best IPL bowling figures",
"Who scored most IPL hundreds",
"Highest IPL team total",
"Lowest IPL team score"

]


AI_INSIGHTS=[

"Teams defending totals win slightly more night games.",
"Spinners dominate middle overs in IPL matches.",
"Powerplay strike rates strongly predict match outcomes.",
"Death over economy is the biggest factor in close IPL games.",
"Chasing teams benefit significantly from dew in night matches.",
"Teams scoring 180+ win most IPL matches historically.",
"Batsmen targeting weak fifth bowlers increase scoring rate.",
"Left-right batting combinations disturb bowling rhythm."

]


STAT_HIGHLIGHTS=[

"Virat Kohli is the all-time leading IPL run scorer.",
"Chris Gayle holds the highest individual IPL score: 175.",
"YS Chahal has taken the most IPL wickets.",
"Mumbai Indians have won the most IPL titles.",
"MS Dhoni has played the most IPL matches.",
"Alzarri Joseph recorded best bowling figures: 6/12.",
"RCB holds the highest team total: 263.",
"RCB also holds the lowest team total: 49."

]


def generate_feed():

    cards=[]

    cards.append({
        "type":"question",
        "title":"Trending Question",
        "text":random.choice(TRENDING_QUESTIONS)
    })

    cards.append({
        "type":"insight",
        "title":"AI Insight",
        "text":random.choice(AI_INSIGHTS)
    })

    cards.append({
        "type":"stat",
        "title":"Stat Highlight",
        "text":random.choice(STAT_HIGHLIGHTS)
    })

    return {"cards":cards}