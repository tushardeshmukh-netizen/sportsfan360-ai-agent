import React,{useState,useEffect,useMemo} from "react";
import {
Radar, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, ResponsiveContainer
} from "recharts";

function PlayerBattle({API_URL}){

const [players,setPlayers]=useState([]);
const [loadingPlayers,setLoadingPlayers]=useState(true);

const [search1,setSearch1]=useState("");
const [search2,setSearch2]=useState("");

const [p1,setP1]=useState("");
const [p2,setP2]=useState("");

const [activeInput,setActiveInput]=useState(null);

const [loading,setLoading]=useState(false);
const [result,setResult]=useState(null);


/* LOAD PLAYERS */

useEffect(()=>{
fetch(`${API_URL}/player-list`)
.then(res=>res.json())
.then(data=>{
setPlayers(data.players || []);
setLoadingPlayers(false);
})
.catch(()=>{
setPlayers([]);
setLoadingPlayers(false);
});
},[API_URL]);


/* FILTER (useMemo FIX) */

const filtered1=useMemo(()=>{
if(search1.length<2) return [];
return players.filter(p=>p.toLowerCase().includes(search1.toLowerCase())).slice(0,15);
},[search1,players]);

const filtered2=useMemo(()=>{
if(search2.length<2) return [];
return players.filter(p=>p.toLowerCase().includes(search2.toLowerCase())).slice(0,15);
},[search2,players]);


/* FETCH */

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
};


/* RADAR */

const getRadarData=(d)=>[
{stat:"Runs",p1:d.stats1.runs,p2:d.stats2.runs},
{stat:"Wickets",p1:d.stats1.wickets,p2:d.stats2.wickets},
{stat:"Sixes",p1:d.stats1.sixes,p2:d.stats2.sixes},
{stat:"Impact",p1:d.impact1,p2:d.impact2}
];


return(

<div className="battleContainer">

<h2>⚔️ Player Battle</h2>

{loadingPlayers && (
<div className="infoBox">⏳ Loading IPL player database...</div>
)}

<div className="battleSelectors">

<div className="searchBox">
<input
value={search1}
placeholder="Search Player 1..."
onFocus={()=>setActiveInput("p1")}
onChange={(e)=>setSearch1(e.target.value)}
/>

{activeInput==="p1" && filtered1.length>0 && (
<div className="dropdownList">
{filtered1.map((p,i)=>(
<div key={i} onClick={()=>{
setP1(p);
setSearch1(p);
}}>
{p}
</div>
))}
</div>
)}

</div>

<div className="vsText">VS</div>

<div className="searchBox">
<input
value={search2}
placeholder="Search Player 2..."
onFocus={()=>setActiveInput("p2")}
onChange={(e)=>setSearch2(e.target.value)}
/>

{activeInput==="p2" && filtered2.length>0 && (
<div className="dropdownList">
{filtered2.map((p,i)=>(
<div key={i} onClick={()=>{
setP2(p);
setSearch2(p);
}}>
{p}
</div>
))}
</div>
)}

</div>

</div>

<div style={{textAlign:"center",marginTop:"10px"}}>
<button className="battleBtn" onClick={startBattle}>
Compare Players
</button>
</div>

{loading && (
<div className="loader">Analyzing performance...</div>
)}

{result && !result.error && (

<div className="battleCard">

<div className="numberGrid">

<div className="numCard">
<h4>{result.player1}</h4>
<p>Runs: {result.stats1.runs}</p>
<p>Wickets: {result.stats1.wickets}</p>
<p>Sixes: {result.stats1.sixes}</p>
</div>

<div className="numCard">
<h4>{result.player2}</h4>
<p>Runs: {result.stats2.runs}</p>
<p>Wickets: {result.stats2.wickets}</p>
<p>Sixes: {result.stats2.sixes}</p>
</div>

</div>

<div style={{height:"300px"}}>
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

<div className="winnerBox">
🏆 Winner: {result.winner}
</div>

</div>

)}

</div>

);

}

export default PlayerBattle;