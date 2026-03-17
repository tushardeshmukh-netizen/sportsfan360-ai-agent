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
const [shot1,setShot1]=useState({off:0,leg:0,straight:0});
const [shot2,setShot2]=useState({off:0,leg:0,straight:0});
const [loading,setLoading]=useState(false);


/* LOAD PLAYERS */

useEffect(()=>{
fetch(`${API_URL}/player-list`)
.then(r=>r.json())
.then(d=>{
if(d && Array.isArray(d.players)){
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
if(!players.length) return [];
return players
.filter(p=>p && p.toLowerCase().includes(search1.toLowerCase()))
.slice(0,10);
},[search1,players]);

const filtered2=useMemo(()=>{
if(!players.length) return [];
return players
.filter(p=>p && p.toLowerCase().includes(search2.toLowerCase()))
.slice(0,10);
},[search2,players]);


/* FETCH */

const startBattle=async()=>{

if(!p1 || !p2 || p1===p2){
alert("Select 2 different players");
return;
}

setLoading(true);

try{

const battleRes=await fetch(`${API_URL}/player-battle?p1=${encodeURIComponent(p1)}&p2=${encodeURIComponent(p2)}`);
const battleData=await battleRes.json();

if(!battleData || battleData.error){
setLoading(false);
return;
}

const s1=await fetch(`${API_URL}/player-shotmap?player=${encodeURIComponent(p1)}`).then(r=>r.json());
const s2=await fetch(`${API_URL}/player-shotmap?player=${encodeURIComponent(p2)}`).then(r=>r.json());

setResult(battleData);
setShot1(s1?.data || {off:0,leg:0,straight:0});
setShot2(s2?.data || {off:0,leg:0,straight:0});

}catch(e){
console.error("Battle error:",e);
}

setLoading(false);
};


/* RADAR SAFE */

const radarData = result ? [
{stat:"Runs",p1:result?.stats1?.runs || 0,p2:result?.stats2?.runs || 0},
{stat:"Wickets",p1:result?.stats1?.wickets || 0,p2:result?.stats2?.wickets || 0},
{stat:"Sixes",p1:result?.stats1?.sixes || 0,p2:result?.stats2?.sixes || 0},
{stat:"Impact",p1:result?.impact1 || 0,p2:result?.impact2 || 0}
] : [];


/* PIE SAFE */

const pie1=[
{name:"Off",value:shot1.off || 0},
{name:"Leg",value:shot1.leg || 0},
{name:"Straight",value:shot1.straight || 0}
];

const pie2=[
{name:"Off",value:shot2.off || 0},
{name:"Leg",value:shot2.leg || 0},
{name:"Straight",value:shot2.straight || 0}
];


return(

<div className="battleContainer">

<h2>⚔️ Player Intelligence Battle</h2>


{/* SEARCH */}

<div className="battleSelectors">

<div>
<input
value={search1}
onChange={(e)=>setSearch1(e.target.value)}
placeholder="Search Player 1"
/>

{filtered1.map((p,i)=>(
<div key={i} onClick={()=>{
setP1(p);
setSearch1(p);
}}>
{p}
</div>
))}

</div>

<div>VS</div>

<div>
<input
value={search2}
onChange={(e)=>setSearch2(e.target.value)}
placeholder="Search Player 2"
/>

{filtered2.map((p,i)=>(
<div key={i} onClick={()=>{
setP2(p);
setSearch2(p);
}}>
{p}
</div>
))}

</div>

</div>


<button onClick={startBattle}>
Compare Players
</button>


{loading && <p>Analyzing...</p>}


{/* RESULT SAFE */}

{result && result.stats1 && result.stats2 && (

<div>

<ResponsiveContainer width="100%" height={300}>
<RadarChart data={radarData}>
<PolarGrid/>
<PolarAngleAxis dataKey="stat"/>
<Radar dataKey="p1" stroke="#ff4d4d" fill="#ff4d4d" fillOpacity={0.5}/>
<Radar dataKey="p2" stroke="#4da6ff" fill="#4da6ff" fillOpacity={0.5}/>
</RadarChart>
</ResponsiveContainer>


<div style={{display:"flex",justifyContent:"space-around"}}>

<PieChart width={200} height={200}>
<Pie data={pie1} dataKey="value">
<Cell fill="#ff4d4d"/>
<Cell fill="#ffa500"/>
<Cell fill="#00ffff"/>
</Pie>
</PieChart>

<PieChart width={200} height={200}>
<Pie data={pie2} dataKey="value">
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