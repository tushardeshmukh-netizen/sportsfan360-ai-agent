from flask import Flask,jsonify,request
from flask_cors import CORS
import random

from feed_engine import generate_feed
from stats_engine import answer_question

app=Flask(__name__)
CORS(app)


@app.route("/")
def home():
    return {"status":"SportsFan360 AI running"}


# ---------------- FEED ----------------

@app.route("/feed")
def feed():

    try:
        data=generate_feed()
        return jsonify(data)

    except Exception as e:

        return jsonify({
            "cards":[
                {
                    "type":"question",
                    "title":"Trending Question",
                    "text":"Highest IPL score"
                },
                {
                    "type":"insight",
                    "title":"AI Insight",
                    "text":"Teams defending totals win slightly more night games."
                },
                {
                    "type":"stat",
                    "title":"Stat Highlight",
                    "text":"Virat Kohli is the all-time leading IPL run scorer."
                }
            ]
        })


# ---------------- ASK AI ----------------

@app.route("/ask")
def ask():

    q=request.args.get("question","")

    try:
        result=answer_question(q)
        return jsonify(result)

    except Exception as e:

        return jsonify({
            "answer":"Unable to analyze IPL data currently",
            "chart_data":[]
        })


# ---------------- TRIVIA ----------------

def generate_trivia():

    questions=[

        {
        "q":"Who has scored the most runs in IPL history?",
        "options":["Virat Kohli","Rohit Sharma","David Warner","MS Dhoni"],
        "answer":"Virat Kohli"
        },

        {
        "q":"Who has taken the most wickets in IPL history?",
        "options":["YS Chahal","Lasith Malinga","Bhuvneshwar Kumar","Amit Mishra"],
        "answer":"YS Chahal"
        },

        {
        "q":"Which team has won the most IPL titles?",
        "options":["Mumbai Indians","Chennai Super Kings","KKR","RCB"],
        "answer":"Mumbai Indians"
        },

        {
        "q":"Who scored the highest individual IPL score?",
        "options":["Chris Gayle","AB de Villiers","Virat Kohli","David Warner"],
        "answer":"Chris Gayle"
        },

        {
        "q":"Which team won the first IPL season?",
        "options":["Rajasthan Royals","CSK","RCB","KKR"],
        "answer":"Rajasthan Royals"
        },

        {
        "q":"Who is known as Captain Cool?",
        "options":["MS Dhoni","Virat Kohli","Rohit Sharma","Gambhir"],
        "answer":"MS Dhoni"
        },

        {
        "q":"Which stadium is home of Mumbai Indians?",
        "options":["Wankhede Stadium","Chepauk","Eden Gardens","Kotla"],
        "answer":"Wankhede Stadium"
        },

        {
        "q":"Who hit the fastest IPL century?",
        "options":["Chris Gayle","KL Rahul","AB de Villiers","Yusuf Pathan"],
        "answer":"Chris Gayle"
        },

        {
        "q":"Which team is called Super Kings?",
        "options":["CSK","MI","RCB","GT"],
        "answer":"CSK"
        },

        {
        "q":"Who is called Universe Boss?",
        "options":["Chris Gayle","Virat Kohli","Warner","Maxwell"],
        "answer":"Chris Gayle"
        }

    ]

    random.shuffle(questions)

    return {"questions":questions}


@app.route("/trivia")
def trivia():
    return jsonify(generate_trivia())


# ---------------- SERVER ----------------

if __name__=="__main__":
    app.run(port=8000)