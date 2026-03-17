import React,{useState,useEffect} from "react";
import {
Radar, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, ResponsiveContainer
} from "recharts";

function PlayerBattle({API_URL}){

const [players,setPlayers]=useState([]);
const [search1,setSearch1]=useState("");
const [search2,setSearch2]=useState("");
const [p1,setP1]=useState("");
const [p2,setP2]=useState("");

const [result,setResult]=useState(null);
const [loading,setLoading]=useState(false);


/* LOAD PLAYERS */

useEffect(()=>{
fetch(`${API_URL}/player-list`)
.then(res=>res.json())
.then(data=>setPlayers(data.players || []))
.catch(()=>setPlayers([]))
},[API_URL])


/* FILTER PLAYERS */

const filterPlayers=(search)=>{
return players
.filter(p=>p.toLowerCase().includes(search.toLowerCase()))
.slice(0,20)
}


/* FETCH BATTLE */

const startBattle=async()=>{
if(!p1 || !p2 || p1===p2) return;

setLoading(true);
setResult(null);

try{
const res=await fetch(`${API_URL}/player-battle?p1=${encodeURIComponent(p1)}&p2=${encodeURIComponent(p2)}`);
const data=await res.json();
setResult(data);
}catch(e){
console.error(e);
}

setLoading(false);
}


/* SWAP */

const swapPlayers=()=>{
setP1(p2);
setP2(p1);
}


/* WIDTH */

const getWidth=(v1,v2)=>{
const max=Math.max(v1,v2,1);
return {
w1:(v1/max)*100,
w2:(v2/max)*100
};
}


/* INSIGHT */

const getInsight=(data)=>{

let insights=[];

if(data.comparison.runs===data.player1){
insights.push(`${data.player1} leads in runs`);
}else{
insights.push(`${data.player2} dominates scoring`);
}

if(data.comparison.sixes===data.player1){
insights.push(`${data.player1} is explosive`);
}else{
insights.push(`${data.player2} hits more sixes`);
}

if(data.comparison.wickets===data.player1){
insights.push(`${data.player1} contributes in bowling`);
}else{
insights.push(`${data.player2} stronger in bowling`);
}

return `${insights.join(", ")}. Overall ${data.winner} leads.`;
}


/* RADAR DATA */

const getRadarData=(data)=>[
{stat:"Runs",p1:data.stats1.runs,p2:data.stats2.runs},
{stat:"Wickets",p1:data.stats1.wickets,p2:data.stats2.wickets},
{stat:"Sixes",p1:data.stats1.sixes,p2:data.stats2.sixes},
{stat:"Impact",p1:data.impact1,p2:data.impact2}
];


return(

<div className="battleContainer">

<div className="battleHeader">
<h2>⚔️ Player Battle</h2>
<p>Search and compare any IPL players across all seasons</p>
</div>


{/* SEARCH SELECTORS */}

<div className="battleSelectors">

<div className="searchBox">

<input
placeholder="Search Player 1..."
value={search1}
onChange={(e)=>setSearch1(e.target.value)}
/>

<div className="dropdownList">
{filterPlayers(search1).map((p,i)=>(
<div key={i} onClick={()=>{setP1(p);setSearch1(p)}}>
{p}
</div>
))}
</div>

</div>

<div className="vsText">VS</div>

<div className="searchBox">

<input
placeholder="Search Player 2..."
value={search2}
onChange={(e)=>setSearch2(e.target.value)}
/>

<div className="dropdownList">
{filterPlayers(search2).map((p,i)=>(
<div key={i} onClick={()=>{setP2(p);setSearch2(p)}}>
{p}
</div>
))}
</div>

</div>

</div>


<div style={{textAlign:"center",marginBottom:"20px"}}>

<button className="battleBtn" onClick={startBattle}>
Compare Players
</button>

<button className="battleBtn" onClick={swapPlayers} style={{marginLeft:"10px"}}>
Swap
</button>

</div>


{/* LOADING */}

{loading && <p style={{textAlign:"center"}}>Analyzing player data...</p>}


{/* RESULT */}

{result && !result.error && (

<div className="battleCard">

<div className="playersRow">
<div className="playerName">{result.player1}</div>
<div className="vsBig">VS</div>
<div className="playerName">{result.player2}</div>
</div>


{/* RADAR */}

<div style={{width:"100%",height:"320px"}}>

<ResponsiveContainer>
<RadarChart data={getRadarData(result)}>
<PolarGrid />
<PolarAngleAxis dataKey="stat" />
<PolarRadiusAxis />

<Radar dataKey="p1" stroke="#ff4d4d" fill="#ff4d4d" fillOpacity={0.5}/>
<Radar dataKey="p2" stroke="#4da6ff" fill="#4da6ff" fillOpacity={0.5}/>

</RadarChart>
</ResponsiveContainer>

</div>


{/* NUMERIC CARDS */}

<div className="numberGrid">

<div className="numCard">
<h4>Runs</h4>
<p>{result.stats1.runs} vs {result.stats2.runs}</p>
</div>

<div className="numCard">
<h4>Wickets</h4>
<p>{result.stats1.wickets} vs {result.stats2.wickets}</p>
</div>

<div className="numCard">
<h4>Sixes</h4>
<p>{result.stats1.sixes} vs {result.stats2.sixes}</p>
</div>

<div className="numCard">
<h4>Impact</h4>
<p>{result.impact1} vs {result.impact2}</p>
</div>

</div>


{/* BARS */}

{(()=>{
const {w1,w2}=getWidth(result.stats1.runs,result.stats2.runs);
return(
<div className="statRowBattle">
<div className="statLabelBattle">Runs</div>
<div className="barDual">
<div className="bar left" style={{width:`${w1}%`}}></div>
<div className="bar right" style={{width:`${w2}%`}}></div>
</div>
</div>
)
})()}


{/* SCORE */}

<div className="scoreBoard">
{result.player1} {result.score[result.player1]} - {result.score[result.player2]} {result.player2}
</div>


{/* WINNER */}

<div className="winnerSection">
<div className="winnerBox">🏆 Winner: {result.winner}</div>
<div className="insightBox">🔥 {getInsight(result)}</div>
</div>

</div>

)}

</div>

);

}

export default PlayerBattle;