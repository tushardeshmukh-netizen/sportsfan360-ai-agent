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
}

}


def get_player_info(name):

    return players.get(name)