import React,{useState,useEffect,useMemo,useRef} from "react";
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

/* ================= STATE ================= */

const [players,setPlayers]=useState([]);
const [loadingPlayers,setLoadingPlayers]=useState(true);

const [search1,setSearch1]=useState("");
const [search2,setSearch2]=useState("");

const [p1,setP1]=useState("");
const [p2,setP2]=useState("");

const [show1,setShow1]=useState(false);
const [show2,setShow2]=useState(false);

const [result,setResult]=useState(null);
const [shot1,setShot1]=useState({off:0,leg:0,straight:0});
const [shot2,setShot2]=useState({off:0,leg:0,straight:0});

const [loading,setLoading]=useState(false);

const ref1=useRef();
const ref2=useRef();

/* ================= LOAD PLAYERS ================= */

useEffect(()=>{
setLoadingPlayers(true);

fetch(`${API_URL}/player-list`)
.then(r=>r.json())
.then(d=>{
setPlayers(d?.players || []);
setLoadingPlayers(false);
})
.catch(()=>{
setPlayers([]);
setLoadingPlayers(false);
});
},[API_URL]);

/* ================= OUTSIDE CLICK ================= */

useEffect(()=>{
const handler=(e)=>{
if(ref1.current && !ref1.current.contains(e.target)) setShow1(false);
if(ref2.current && !ref2.current.contains(e.target)) setShow2(false);
};
document.addEventListener("click",handler);
return ()=>document.removeEventListener("click",handler);
},[]);

/* ================= FILTER ================= */

const filtered1=useMemo(()=>{
if(!search1) return [];
return players
.filter(p=>p.toLowerCase().includes(search1.toLowerCase()))
.slice(0,15);
},[search1,players]);

const filtered2=useMemo(()=>{
if(!search2) return [];
return players
.filter(p=>p.toLowerCase().includes(search2.toLowerCase()))
.slice(0,15);
},[search2,players]);

/* ================= FETCH ================= */

const startBattle=async()=>{

if(!p1 || !p2 || p1===p2){
alert("Select 2 different players");
return;
}

setLoading(true);

try{

const battle=await fetch(`${API_URL}/player-battle?p1=${encodeURIComponent(p1)}&p2=${encodeURIComponent(p2)}`).then(r=>r.json());

const s1=await fetch(`${API_URL}/player-shotmap?player=${encodeURIComponent(p1)}`).then(r=>r.json());
const s2=await fetch(`${API_URL}/player-shotmap?player=${encodeURIComponent(p2)}`).then(r=>r.json());

setResult(battle);
setShot1(s1?.data || {off:0,leg:0,straight:0});
setShot2(s2?.data || {off:0,leg:0,straight:0});

}catch(e){
console.error(e);
}

setLoading(false);
};

/* ================= RADAR ================= */

const radarData = result ? [
{stat:"Runs",p1:result.stats1.runs,p2:result.stats2.runs},
{stat:"Wickets",p1:result.stats1.wickets,p2:result.stats2.wickets},
{stat:"Sixes",p1:result.stats1.sixes,p2:result.stats2.sixes},
{stat:"SR",p1:result.stats1.strike_rate,p2:result.stats2.strike_rate},
{stat:"Avg",p1:result.stats1.average,p2:result.stats2.average}
] : [];

/* ================= PIE ================= */

const pie1=[
{name:"Off",value:shot1.off},
{name:"Leg",value:shot1.leg},
{name:"Straight",value:shot1.straight}
];

const pie2=[
{name:"Off",value:shot2.off},
{name:"Leg",value:shot2.leg},
{name:"Straight",value:shot2.straight}
];

/* ================= HELPER ================= */

const getClass=(v1,v2)=>{
if(v1>v2) return "statBox win";
if(v1<v2) return "statBox lose";
return "statBox";
};

/* ================= UI ================= */

return(

<div className="battleContainer">

<div className="battleHeader">
<h2>⚔️ Player Intelligence Battle</h2>
<p>Compare full IPL performance across seasons</p>
</div>

{/* LOADING */}
{loadingPlayers && <p className="loadingText">Loading IPL player database...</p>}

/* ================= SELECTORS ================= */

<div className="battleSelectors">

{/* PLAYER 1 */}
<div className="dropdown" ref={ref1}>

<input
className="battleInput"
value={search1}
placeholder={loadingPlayers ? "Loading..." : "Search Player 1"}
disabled={loadingPlayers}
onFocus={()=>setShow1(true)}
onChange={(e)=>{
setSearch1(e.target.value);
setP1("");
}}
/>

{show1 && filtered1.length>0 && (
<div className="dropdownList">
{filtered1.map((p,i)=>(
<div key={i} className="dropdownItem" onClick={()=>{
setP1(p);
setSearch1(p);
setShow1(false);
}}>
{p}
</div>
))}
</div>
)}

</div>

<div className="vs">VS</div>

{/* PLAYER 2 */}
<div className={`dropdown ${!p1 ? "disabled":""}`} ref={ref2}>

<input
className="battleInput"
value={search2}
placeholder={!p1 ? "Select Player 1 first" : "Search Player 2"}
disabled={!p1}
onFocus={()=>p1 && setShow2(true)}
onChange={(e)=>{
setSearch2(e.target.value);
setP2("");
}}
/>

{show2 && filtered2.length>0 && (
<div className="dropdownList">
{filtered2.map((p,i)=>(
<div key={i} className="dropdownItem" onClick={()=>{
setP2(p);
setSearch2(p);
setShow2(false);
}}>
{p}
</div>
))}
</div>
)}

</div>

</div>

<button className="compareBtn" onClick={startBattle} disabled={!p1 || !p2}>
Compare Players
</button>

{loading && <p className="loadingText">Analyzing performance...</p>}

/* ================= RESULT ================= */

{result && result.stats1 && result.stats2 && (

<div className="resultCard">

{/* PLAYER NAMES */}
<div className="playersRow">
<div className="playerName">{p1}</div>
<div className="vsBig">VS</div>
<div className="playerName">{p2}</div>
</div>

{/* STATS GRID */}
<div className="statsGrid">

<div className={getClass(result.stats1.runs,result.stats2.runs)}>
<div className="statTitle">Runs</div>
<div className="statValueBig">{result.stats1.runs} | {result.stats2.runs}</div>
</div>

<div className={getClass(result.stats1.wickets,result.stats2.wickets)}>
<div className="statTitle">Wickets</div>
<div className="statValueBig">{result.stats1.wickets} | {result.stats2.wickets}</div>
</div>

<div className={getClass(result.stats1.sixes,result.stats2.sixes)}>
<div className="statTitle">Sixes</div>
<div className="statValueBig">{result.stats1.sixes} | {result.stats2.sixes}</div>
</div>

<div className={getClass(result.stats1.fours,result.stats2.fours)}>
<div className="statTitle">Fours</div>
<div className="statValueBig">{result.stats1.fours} | {result.stats2.fours}</div>
</div>

<div className={getClass(result.stats1.strike_rate,result.stats2.strike_rate)}>
<div className="statTitle">Strike Rate</div>
<div className="statValueBig">{result.stats1.strike_rate} | {result.stats2.strike_rate}</div>
</div>

<div className={getClass(result.stats1.average,result.stats2.average)}>
<div className="statTitle">Average</div>
<div className="statValueBig">{result.stats1.average} | {result.stats2.average}</div>
</div>

<div className={getClass(result.stats1.matches,result.stats2.matches)}>
<div className="statTitle">Matches</div>
<div className="statValueBig">{result.stats1.matches} | {result.stats2.matches}</div>
</div>

</div>

{/* RADAR */}
<ResponsiveContainer width="100%" height={300}>
<RadarChart data={radarData}>
<PolarGrid/>
<PolarAngleAxis dataKey="stat"/>
<Radar dataKey="p1" stroke="#FE2165" fill="#FE2165" fillOpacity={0.4}/>
<Radar dataKey="p2" stroke="#4da6ff" fill="#4da6ff" fillOpacity={0.4}/>
</RadarChart>
</ResponsiveContainer>

{/* PIE */}
<div className="pieContainer">

<PieChart width={200} height={200}>
<Pie data={pie1} dataKey="value">
<Cell fill="#FE2165"/>
<Cell fill="#FD6E0C"/>
<Cell fill="#22c55e"/>
</Pie>
</PieChart>

<PieChart width={200} height={200}>
<Pie data={pie2} dataKey="value">
<Cell fill="#4da6ff"/>
<Cell fill="#60a5fa"/>
<Cell fill="#22c55e"/>
</Pie>
</PieChart>

</div>

{/* WINNER */}
<div className="winner">
🏆 Winner: <span>{result.winner}</span>
</div>

</div>

)}

</div>

);

}

export default PlayerBattle;