import React,{useState,useEffect} from "react";
import {
Radar, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, ResponsiveContainer
} from "recharts";

function PlayerBattle({API_URL}){

const [players,setPlayers]=useState([]);
const [search1,setSearch1]=useState("");
const [search2,setSearch2]=useState("");

const [filtered1,setFiltered1]=useState([]);
const [filtered2,setFiltered2]=useState([]);

const [p1,setP1]=useState("");
const [p2,setP2]=useState("");

const [loading,setLoading]=useState(false);
const [result,setResult]=useState(null);


/* LOAD PLAYERS */

useEffect(()=>{
fetch(`${API_URL}/player-list`)
.then(res=>res.json())
.then(data=>setPlayers(data.players || []))
.catch(()=>setPlayers([]));
},[API_URL])


/* SEARCH */

const filter=(val)=>players.filter(p=>p.toLowerCase().includes(val.toLowerCase())).slice(0,10);

useEffect(()=>{setFiltered1(search1.length>1?filter(search1):[])},[search1]);
useEffect(()=>{setFiltered2(search2.length>1?filter(search2):[])},[search2]);


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
}


/* RADAR */

const getRadarData=(d)=>[
{stat:"Runs",p1:d.stats1.runs,p2:d.stats2.runs},
{stat:"Wickets",p1:d.stats1.wickets,p2:d.stats2.wickets},
{stat:"Sixes",p1:d.stats1.sixes,p2:d.stats2.sixes},
{stat:"Impact",p1:d.impact1,p2:d.impact2}
];


/* 🔥 FAKE WAGON DATA (replace later with real) */

const getWagonData=(player)=>{
return [
{angle:0,value:Math.random()*10},
{angle:45,value:Math.random()*10},
{angle:90,value:Math.random()*10},
{angle:135,value:Math.random()*10},
{angle:180,value:Math.random()*10},
{angle:225,value:Math.random()*10},
{angle:270,value:Math.random()*10},
{angle:315,value:Math.random()*10}
];
};


/* 🔥 FAKE PITCH MAP */

const getPitchMap=()=>{
return Array.from({length:20},()=>({
x:Math.random()*100,
y:Math.random()*100
}));
};


return(

<div className="battleContainer">

<h2>⚔️ Player Battle</h2>


{/* SEARCH */}

<div className="battleSelectors">

<div className="searchBox">
<input value={search1} placeholder="Player 1" onChange={(e)=>setSearch1(e.target.value)}/>
{filtered1.length>0 && (
<div className="dropdownList">
{filtered1.map((p,i)=>(
<div key={i} onClick={()=>{setP1(p);setSearch1(p);setFiltered1([])}}>{p}</div>
))}
</div>
)}
</div>

<div className="vsText">VS</div>

<div className="searchBox">
<input value={search2} placeholder="Player 2" onChange={(e)=>setSearch2(e.target.value)}/>
{filtered2.length>0 && (
<div className="dropdownList">
{filtered2.map((p,i)=>(
<div key={i} onClick={()=>{setP2(p);setSearch2(p);setFiltered2([])}}>{p}</div>
))}
</div>
)}
</div>

</div>


<div style={{textAlign:"center",marginTop:"10px"}}>
<button className="battleBtn" onClick={startBattle}>Compare</button>
</div>


{/* LOADING */}

{loading && <div className="loader">Analyzing...</div>}


/* RESULT */

{result && (

<div className="battleCard">

{/* RADAR */}

<div style={{height:"250px"}}>
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


{/* 🟢 WAGON WHEEL */}

<div className="sectionTitle">🟢 Wagon Wheel</div>

<div className="wagonContainer">

{getWagonData(p1).map((d,i)=>(
<div
key={i}
className="wagonLine red"
style={{
transform:`rotate(${d.angle}deg)`,
height:`${d.value*10}px`
}}
></div>
))}

</div>


{/* 🔵 PITCH MAP */}

<div className="sectionTitle">🔵 Pitch Map</div>

<div className="pitchMap">

{getPitchMap().map((d,i)=>(
<div
key={i}
className="pitchDot"
style={{
left:`${d.x}%`,
top:`${d.y}%`
}}
></div>
))}

</div>


{/* WINNER */}

<div className="winnerBox">
🏆 {result.winner}
</div>

</div>

)}

</div>

);

}

export default PlayerBattle;