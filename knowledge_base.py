<<<<<<< HEAD
players={

"Chris Gayle":{
"country":"West Indies",
"role":"Batsman",
"nickname":"Universe Boss"
},

"Virat Kohli":{
"country":"India",
"role":"Batsman",
"team":"Royal Challengers Bangalore"
},

"Rohit Sharma":{
"country":"India",
"role":"Batsman",
"team":"Mumbai Indians"
=======
player_db={

"virat kohli":{
"role":"Batsman",
"team":"Royal Challengers Bangalore",
"fact":"Highest run scorer in IPL history."
},

"rohit sharma":{
"role":"Batsman",
"team":"Mumbai Indians",
"fact":"Five IPL titles as captain."
},

"ms dhoni":{
"role":"Wicketkeeper",
"team":"Chennai Super Kings",
"fact":"One of the most successful IPL captains."
>>>>>>> agent-v4
}

}


<<<<<<< HEAD
def get_player_info(name):

    return players.get(name)
=======
def get_player_info(question):

    q=question.lower()

    for name in player_db:

        if name in q:

            p=player_db[name]

            return {
            "chart_title":"",
            "chart_data":[],
            "answer":f"{name.title()} is a {p['role']} who plays for {p['team']}. {p['fact']}"
            }

    return None
>>>>>>> agent-v4
