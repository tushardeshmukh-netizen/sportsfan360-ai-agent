import React,{useState,useEffect,useMemo} from "react";
import {Radar,RadarChart,PolarGrid,PolarAngleAxis,ResponsiveContainer,PieChart,Pie,Cell} from "recharts";

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

useEffect(()=>{
fetch(`${API_URL}/player-list`)
.then(r=>r.json())
.then(d=>setPlayers(d.players||[]));
},[API_URL]);

const filtered1=useMemo(()=>players.filter(p=>p.toLowerCase().includes(search1.toLowerCase())).slice(0,10),[search1,players]);
const filtered2=useMemo(()=>players.filter(p=>p.toLowerCase().includes(search2.toLowerCase())).slice(0,10),[search2,players]);

const startBattle=async()=>{
setLoading(true);

const b=await fetch(`${API_URL}/player-battle?p1=${p1}&p2=${p2}`).then(r=>r.json());
const s1=await fetch(`${API_URL}/player-shotmap?player=${p1}`).then(r=>r.json());
const s2=await fetch(`${API_URL}/player-shotmap?player=${p2}`).then(r=>r.json());

setResult(b);
setShot1(s1.data);
setShot2(s2.data);
setLoading(false);
};

const radar=(d)=>[
{stat:"Runs",p1:d.stats1.runs,p2:d.stats2.runs},
{stat:"Wickets",p1:d.stats1.wickets,p2:d.stats2.wickets},
{stat:"Sixes",p1:d.stats1.sixes,p2:d.stats2.sixes},
{stat:"Impact",p1:d.impact1,p2:d.impact2}
];

const pie=(d)=>[
{name:"Off",value:d.off||0},
{name:"Leg",value:d.leg||0},
{name:"Straight",value:d.straight||0}
];

return(
<div className="battleContainer">

<h2>⚔️ Player Intelligence Battle</h2>

<div className="battleSelectors">

<div>
<input value={search1} onChange={(e)=>setSearch1(e.target.value)} placeholder="Player 1"/>
{filtered1.map((p,i)=>(<div key={i} onClick={()=>{setP1(p);setSearch1(p)}}>{p}</div>))}
</div>

<div>VS</div>

<div>
<input value={search2} onChange={(e)=>setSearch2(e.target.value)} placeholder="Player 2"/>
{filtered2.map((p,i)=>(<div key={i} onClick={()=>{setP2(p);setSearch2(p)}}>{p}</div>))}
</div>

</div>

<button onClick={startBattle}>Compare</button>

{loading && <p>Analyzing...</p>}

{result && (
<div>

<ResponsiveContainer height={300}>
<RadarChart data={radar(result)}>
<PolarGrid/>
<PolarAngleAxis dataKey="stat"/>
<Radar dataKey="p1" stroke="red" fill="red"/>
<Radar dataKey="p2" stroke="blue" fill="blue"/>
</RadarChart>
</ResponsiveContainer>

<div style={{display:"flex"}}>

<PieChart width={200} height={200}>
<Pie data={pie(shot1)} dataKey="value">
<Cell fill="red"/><Cell fill="orange"/><Cell fill="cyan"/>
</Pie>
</PieChart>

<PieChart width={200} height={200}>
<Pie data={pie(shot2)} dataKey="value">
<Cell fill="red"/><Cell fill="orange"/><Cell fill="cyan"/>
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