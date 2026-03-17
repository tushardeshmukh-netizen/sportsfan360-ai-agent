import React,{useState,useEffect,useMemo} from "react";
import {
Radar,
RadarChart,
PolarGrid,
PolarAngleAxis,
ResponsiveContainer,
PieChart,
Pie,
Cell
} from "recharts";

function PlayerBattle({API_URL}){

const [players,setPlayers]=useState([]);
const [search1,setSearch1]=useState("");
const [search2,setSearch2]=useState("");
const [p1,setP1]=useState("");
const [p2,setP2]=useState("");
const [result,setResult]=useState(null);
const [shot1,setShot1]=useState({});
const [shot2,setShot2]=useState({});
const [loading,setLoading]=useState(false);
const [error,setError]=useState(null);


/* LOAD PLAYERS */

useEffect(()=>{
fetch(`${API_URL}/player-list`)
.then(r=>r.json())
.then(d=>{
if(d && d.players){
setPlayers(d.players);
}else{
setPlayers([]);
}
})
.catch(()=>{
setPlayers([]);
});
},[API_URL]);


/* FILTER SAFE */

const filtered1=useMemo(()=>{
if(!players || players.length===0) return [];
return players
.filter(p=>p && p.toLowerCase().includes(search1.toLowerCase()))
.slice(0,10);
},[search1,players]);

const filtered2=useMemo(()=>{
if(!players || players.length===0) return [];
return players
.filter(p=>p && p.toLowerCase().includes(search2.toLowerCase()))
.slice(0,10);
},[search2,players]);


/* FETCH BATTLE */

const startBattle=async()=>{

if(!p1 || !p2 || p1===p2){
alert("Select 2 different players");
return;
}

setLoading(true);
setError(null);

try{

const bRes=await fetch(`${API_URL}/player-battle?p1=${encodeURIComponent(p1)}&p2=${encodeURIComponent(p2)}`);
const b=await bRes.json();

const s1Res=await fetch(`${API_URL}/player-shotmap?player=${encodeURIComponent(p1)}`);
const s1=await s1Res.json();

const s2Res=await fetch(`${API_URL}/player-shotmap?player=${encodeURIComponent(p2)}`);
const s2=await s2Res.json();

if(!b || b.error){
setError("Battle data failed");
setLoading(false);
return;
}

setResult(b);
setShot1(s1?.data || {});
setShot2(s2?.data || {});

}catch(e){
console.error(e);
setError("API failed");
}

setLoading(false);
};


/* SAFE RADAR */

const radar=(d)=>{
if(!d || !d.stats1 || !d.stats2) return [];
return [
{stat:"Runs",p1:d.stats1.runs||0,p2:d.stats2.runs||0},
{stat:"Wickets",p1:d.stats1.wickets||0,p2:d.stats2.wickets||0},
{stat:"Sixes",p1:d.stats1.sixes||0,p2:d.stats2.sixes||0},
{stat:"Impact",p1:d.impact1||0,p2:d.impact2||0}
];
};


/* SAFE PIE */

const pie=(d)=>{
return [
{name:"Off",value:d?.off||0},
{name:"Leg",value:d?.leg||0},
{name:"Straight",value:d?.straight||0}
];
};


return(

<div className="battleContainer">

<h2>⚔️ Player Intelligence Battle</h2>


{/* SEARCH */}

<div className="battleSelectors">

<div>
<input
value={search1}
onChange={(e)=>setSearch1(e.target.value)}
placeholder="Player 1"
/>

{filtered1.map((p,i)=>(
<div
key={i}
onClick={()=>{
setP1(p);
setSearch1(p);
}}
>
{p}
</div>
))}

</div>

<div>VS</div>

<div>
<input
value={search2}
onChange={(e)=>setSearch2(e.target.value)}
placeholder="Player 2"
/>

{filtered2.map((p,i)=>(
<div
key={i}
onClick={()=>{
setP2(p);
setSearch2(p);
}}
>
{p}
</div>
))}

</div>

</div>


{/* BUTTON */}

<button onClick={startBattle}>
Compare
</button>


{/* LOADING */}

{loading && <p>Analyzing...</p>}


{/* ERROR */}

{error && <p style={{color:"red"}}>{error}</p>}


{/* RESULT */}

{result && !error && (

<div>

<ResponsiveContainer width="100%" height={300}>
<RadarChart data={radar(result)}>
<PolarGrid/>
<PolarAngleAxis dataKey="stat"/>

<Radar dataKey="p1" stroke="#ff4d4d" fill="#ff4d4d" fillOpacity={0.5}/>
<Radar dataKey="p2" stroke="#4da6ff" fill="#4da6ff" fillOpacity={0.5}/>

</RadarChart>
</ResponsiveContainer>


<div style={{display:"flex",justifyContent:"space-around"}}>

<PieChart width={200} height={200}>
<Pie data={pie(shot1)} dataKey="value">
<Cell fill="#ff4d4d"/>
<Cell fill="#ffa500"/>
<Cell fill="#00ffff"/>
</Pie>
</PieChart>

<PieChart width={200} height={200}>
<Pie data={pie(shot2)} dataKey="value">
<Cell fill="#4da6ff"/>
<Cell fill="#ffa500"/>
<Cell fill="#00ffff"/>
</Pie>
</PieChart>

</div>


<h3>🏆 {result.winner}</h3>

</div>

)}

</div>

);

}

export default PlayerBattle;