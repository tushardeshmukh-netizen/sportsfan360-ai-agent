from flask import Blueprint, request, jsonify
import random

daily_challenge = Blueprint("daily_challenge", __name__)

@daily_challenge.route("/daily-challenge")
def get_daily_challenge():

    match_id = request.args.get("matchId", "default")

    team1 = "MI"
    team2 = "CSK"

    # DEMO PLAYERS
    batsmen = ["Rohit Sharma", "Suryakumar Yadav", "MS Dhoni", "Ruturaj Gaikwad"]
    bowlers = ["Bumrah", "Jadeja", "Pathirana", "Chahar"]

    data = {
        "matchId": match_id,
        "questions": [
            {
                "id": "winner",
                "question": "🏆 Who will win?",
                "options": [team1, team2]
            },
            {
                "id": "top_batsman",
                "question": "🔥 Top Batsman?",
                "options": batsmen
            },
            {
                "id": "top_bowler",
                "question": "🎯 Top Bowler?",
                "options": bowlers
            },
            {
                "id": "total_runs",
                "question": "💥 Total Runs?",
                "options": ["<150", "150-170", "170-190", "190+"]
            },
            {
                "id": "toss",
                "question": "⚡ Toss Winner?",
                "options": [team1, team2]
            },
            {
                "id": "powerplay",
                "question": "🎯 Powerplay Score?",
                "options": ["<40", "40-60", "60-80", "80+"]
            }
        ]
    }

    return jsonify(data)