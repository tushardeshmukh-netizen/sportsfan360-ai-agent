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

/* LOAD PLAYERS */
useEffect(()=>{
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

/* CLOSE DROPDOWN */
useEffect(()=>{
const handler=(e)=>{
if(ref1.current && !ref1.current.contains(e.target)) setShow1(false);
if(ref2.current && !ref2.current.contains(e.target)) setShow2(false);
};
document.addEventListener("click",handler);
return ()=>document.removeEventListener("click",handler);
},[]);

/* FILTER */
const filtered1=useMemo(()=>{
return players.filter(p=>p.toLowerCase().includes(search1.toLowerCase())).slice(0,20);
},[search1,players]);

const filtered2=useMemo(()=>{
return players.filter(p=>p.toLowerCase().includes(search2.toLowerCase())).slice(0,20);
},[search2,players]);

/* FETCH */
const startBattle=async()=>{
if(!p1 || !p2 || p1===p2){
alert("Select 2 different players");
return;
}

setLoading(true);

const battle=await fetch(`${API_URL}/player-battle?p1=${p1}&p2=${p2}`).then(r=>r.json());
const s1=await fetch(`${API_URL}/player-shotmap?player=${p1}`).then(r=>r.json());
const s2=await fetch(`${API_URL}/player-shotmap?player=${p2}`).then(r=>r.json());

setResult(battle);
setShot1(s1.data);
setShot2(s2.data);

setLoading(false);
};

/* DATA */
const radarData = result ? [
{stat:"Runs",p1:result.stats1.runs,p2:result.stats2.runs},
{stat:"Wickets",p1:result.stats1.wickets,p2:result.stats2.wickets},
{stat:"Sixes",p1:result.stats1.sixes,p2:result.stats2.sixes},
{stat:"Impact",p1:result.impact1,p2:result.impact2}
] : [];

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

return(

<div className="battleContainer">

<h2>⚔️ Player Intelligence Battle</h2>

{loadingPlayers && <p>Loading players...</p>}

<div className="battleSelectors">

{/* PLAYER 1 */}
<div className="dropdown" ref={ref1}>
<div className="dropdownHeader" onClick={()=>setShow1(true)}>
{p1 || "Select Player 1"}
</div>

{show1 && (
<div className="dropdownMenu">
<input
value={search1}
placeholder="Search player..."
onChange={(e)=>setSearch1(e.target.value)}
/>

<div className="list">
{filtered1.map((p,i)=>(
<div key={i} onClick={()=>{
setP1(p);
setSearch1(p);
setShow1(false);
}}>
{p}
</div>
))}
</div>
</div>
)}
</div>

<div>VS</div>

{/* PLAYER 2 */}
<div className="dropdown" ref={ref2}>
<div className="dropdownHeader" onClick={()=>p1 && setShow2(true)}>
{p2 || (p1 ? "Select Player 2" : "Select Player 1 first")}
</div>

{show2 && (
<div className="dropdownMenu">
<input
value={search2}
placeholder="Search player..."
onChange={(e)=>setSearch2(e.target.value)}
/>

<div className="list">
{filtered2.map((p,i)=>(
<div key={i} onClick={()=>{
setP2(p);
setSearch2(p);
setShow2(false);
}}>
{p}
</div>
))}
</div>
</div>
)}
</div>

</div>

<button onClick={startBattle} disabled={!p1 || !p2}>
Compare Players
</button>

{loading && <p>Analyzing...</p>}

{result && (
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

<h3>🏆 Winner: {result.winner}</h3>

</div>
)}

</div>

);

}

export default PlayerBattle;