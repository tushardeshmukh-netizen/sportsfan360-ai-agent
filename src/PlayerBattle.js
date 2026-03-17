import React,{useState,useEffect} from "react";
import {
Radar, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, ResponsiveContainer
} from "recharts";

function PlayerBattle({API_URL}){

const [players,setPlayers]=useState([]);
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


/* BAR WIDTH */

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
<p>Select any two IPL players and compare their stats</p>
</div>


{/* SELECTORS */}

<div className="battleSelectors">

<select value={p1} onChange={(e)=>setP1(e.target.value)}>
<option value="">Select Player 1</option>
{players.map((p,i)=>(
<option key={i} value={p}>{p}</option>
))}
</select>

<div className="vsText">VS</div>

<select value={p2} onChange={(e)=>setP2(e.target.value)}>
<option value="">Select Player 2</option>
{players.map((p,i)=>(
<option key={i} value={p}>{p}</option>
))}
</select>

</div>


<div style={{textAlign:"center",marginBottom:"15px"}}>

<button className="battleBtn" onClick={startBattle}>
Compare Players
</button>

<button className="battleBtn" onClick={swapPlayers} style={{marginLeft:"10px"}}>
Swap
</button>

</div>


{/* LOADING */}

{loading && (
<p style={{textAlign:"center"}}>Analyzing...</p>
)}


{/* RESULT */}

{result && !result.error && (

<div className="battleCard">

<div className="playersRow">
<div className="playerName">{result.player1}</div>
<div className="vsBig">VS</div>
<div className="playerName">{result.player2}</div>
</div>


{/* RADAR */}

<div style={{width:"100%",height:"300px"}}>

<ResponsiveContainer>
<RadarChart data={getRadarData(result)}>
<PolarGrid />
<PolarAngleAxis dataKey="stat" />
<PolarRadiusAxis />

<Radar name={result.player1} dataKey="p1" stroke="#ff4d4d" fill="#ff4d4d" fillOpacity={0.5}/>
<Radar name={result.player2} dataKey="p2" stroke="#4da6ff" fill="#4da6ff" fillOpacity={0.5}/>

</RadarChart>
</ResponsiveContainer>

</div>


{/* RUNS */}

{(()=>{
const {w1,w2}=getWidth(result.stats1.runs,result.stats2.runs);
return(
<div className="statRowBattle">
<div className="statLabelBattle">
Runs {result.comparison.runs===result.player1 ? "🏆" : ""}
</div>
<div className="statBars">
<span className="statValue">{result.stats1.runs}</span>
<div className="barContainer"><div className="bar" style={{width:`${w1}%`}}></div></div>
<div className="barContainer"><div className="bar" style={{width:`${w2}%`}}></div></div>
<span className="statValue">{result.stats2.runs}</span>
</div>
</div>
)
})()}


{/* WICKETS */}

{(()=>{
const {w1,w2}=getWidth(result.stats1.wickets,result.stats2.wickets);
return(
<div className="statRowBattle">
<div className="statLabelBattle">
Wickets {result.comparison.wickets===result.player1 ? "🏆" : ""}
</div>
<div className="statBars">
<span className="statValue">{result.stats1.wickets}</span>
<div className="barContainer"><div className="bar" style={{width:`${w1}%`}}></div></div>
<div className="barContainer"><div className="bar" style={{width:`${w2}%`}}></div></div>
<span className="statValue">{result.stats2.wickets}</span>
</div>
</div>
)
})()}


{/* SIXES */}

{(()=>{
const {w1,w2}=getWidth(result.stats1.sixes,result.stats2.sixes);
return(
<div className="statRowBattle">
<div className="statLabelBattle">
Sixes {result.comparison.sixes===result.player1 ? "🏆" : ""}
</div>
<div className="statBars">
<span className="statValue">{result.stats1.sixes}</span>
<div className="barContainer"><div className="bar" style={{width:`${w1}%`}}></div></div>
<div className="barContainer"><div className="bar" style={{width:`${w2}%`}}></div></div>
<span className="statValue">{result.stats2.sixes}</span>
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