import React,{useState,useEffect} from "react";
import {
Radar, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, ResponsiveContainer
} from "recharts";

function PlayerBattle({API_URL}){

const [players,setPlayers]=useState([]);
const [filtered1,setFiltered1]=useState([]);
const [filtered2,setFiltered2]=useState([]);

const [search1,setSearch1]=useState("");
const [search2,setSearch2]=useState("");

const [p1,setP1]=useState("");
const [p2,setP2]=useState("");

const [loading,setLoading]=useState(false);
const [searching,setSearching]=useState(false);
const [result,setResult]=useState(null);


/* LOAD PLAYERS */

useEffect(()=>{
fetch(`${API_URL}/player-list`)
.then(res=>res.json())
.then(data=>setPlayers(data.players || []))
.catch(()=>setPlayers([]))
},[API_URL])


/* DEBOUNCED SEARCH */

useEffect(()=>{
if(search1.length<2){
setFiltered1([]);
return;
}

setSearching(true);

const t=setTimeout(()=>{
const res=players
.filter(p=>p.toLowerCase().includes(search1.toLowerCase()))
.slice(0,10);
setFiltered1(res);
setSearching(false);
},300);

return ()=>clearTimeout(t);

},[search1,players])


useEffect(()=>{
if(search2.length<2){
setFiltered2([]);
return;
}

setSearching(true);

const t=setTimeout(()=>{
const res=players
.filter(p=>p.toLowerCase().includes(search2.toLowerCase()))
.slice(0,10);
setFiltered2(res);
setSearching(false);
},300);

return ()=>clearTimeout(t);

},[search2,players])


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


/* SWAP */

const swapPlayers=()=>{
setP1(p2);
setP2(p1);
setSearch1(p2);
setSearch2(p1);
}


/* WIDTH */

const getWidth=(v1,v2)=>{
const max=Math.max(v1,v2,1);
return {
w1:(v1/max)*100,
w2:(v2/max)*100
};
}


/* RADAR */

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


{/* SEARCH */}

<div className="battleSelectors">

{/* PLAYER 1 */}

<div className="searchBox">

<input
placeholder="Type player name (min 2 letters)"
value={search1}
onChange={(e)=>setSearch1(e.target.value)}
/>

{search1.length<2 && (
<div className="hint">Start typing…</div>
)}

{searching && <div className="hint">Searching...</div>}

{filtered1.length>0 && (
<div className="dropdownList">
{filtered1.map((p,i)=>(
<div key={i} onClick={()=>{
setP1(p);
setSearch1(p);
setFiltered1([]);
}}>
{p}
</div>
))}
</div>
)}

</div>


<div className="vsText">VS</div>


{/* PLAYER 2 */}

<div className="searchBox">

<input
placeholder="Type player name"
value={search2}
onChange={(e)=>setSearch2(e.target.value)}
/>

{search2.length<2 && (
<div className="hint">Start typing…</div>
)}

{searching && <div className="hint">Searching...</div>}

{filtered2.length>0 && (
<div className="dropdownList">
{filtered2.map((p,i)=>(
<div key={i} onClick={()=>{
setP2(p);
setSearch2(p);
setFiltered2([]);
}}>
{p}
</div>
))}
</div>
)}

</div>

</div>


<div style={{textAlign:"center",marginTop:"15px"}}>

<button className="battleBtn" onClick={startBattle}>
Compare Players
</button>

<button className="battleBtn" onClick={swapPlayers} style={{marginLeft:"10px"}}>
Swap
</button>

</div>


{/* LOADING */}

{loading && (
<div className="loader">
Analyzing player stats...
</div>
)}


{/* RESULT */}

{result && !result.error && (

<div className="battleCard">

<div className="playersRow">
<div className="playerName">{result.player1}</div>
<div className="vsBig">VS</div>
<div className="playerName">{result.player2}</div>
</div>


<div style={{width:"100%",height:"300px"}}>
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

</div>

)}

</div>

);

}

export default PlayerBattle;