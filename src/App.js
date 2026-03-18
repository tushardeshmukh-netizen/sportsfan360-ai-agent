import React,{useState,useRef,useEffect} from "react";
import "./App.css";
import logo from "./assets/logo.png";
import Trivia from "./Trivia";
import PlayerBattle from "./PlayerBattle";

const statsPool=[
{label:"Most IPL Runs",value:"Virat Kohli",num:"8671"},
{label:"Most IPL Wickets",value:"YS Chahal",num:"229"},
{label:"Most IPL Titles",value:"Mumbai Indians",num:"5"},
{label:"Most IPL Sixes",value:"Chris Gayle",num:"357"},
{label:"Highest IPL Score",value:"Chris Gayle",num:"175"},
{label:"Most IPL Hundreds",value:"Virat Kohli",num:"7"},
{label:"Most IPL Matches",value:"MS Dhoni",num:"250+"},
{label:"Best Bowling Figures",value:"Alzarri Joseph",num:"6/12"},
{label:"Fastest IPL Fifty",value:"KL Rahul",num:"14 balls"},
{label:"Fastest IPL Century",value:"Chris Gayle",num:"30 balls"},
{label:"Most Dot Balls",value:"Bhuvneshwar Kumar",num:"1500+"},
{label:"Most Hat-tricks",value:"Amit Mishra",num:"3"},
{label:"Most Catches",value:"Suresh Raina",num:"109"},
{label:"Highest Team Total",value:"RCB",num:"263"},
{label:"Lowest Team Total",value:"RCB",num:"49"}
];

function App(){

const API_URL="https://sportsfan360-ai-agent-1.onrender.com";

const [activeTab,setActiveTab]=useState("home");
const [feed,setFeed]=useState(null);

const [question,setQuestion]=useState("");
const [messages,setMessages]=useState([]);
const [loading,setLoading]=useState(false);

const chatEndRef=useRef();
const [stats,setStats]=useState(statsPool.slice(0,3));

const [speaking,setSpeaking]=useState(false);
const [listening,setListening]=useState(false);

// ================= SPEAK =================
const speakText=(text)=>{
if(!("speechSynthesis" in window)) return;
window.speechSynthesis.cancel();
const u=new SpeechSynthesisUtterance(text);
u.lang="en-IN";
u.onstart=()=>setSpeaking(true);
u.onend=()=>setSpeaking(false);
window.speechSynthesis.speak(u);
};

// ================= LIVE MATCH =================
const [liveMatches,setLiveMatches]=useState([]);
const [selectedMatch,setSelectedMatch]=useState(null);

useEffect(()=>{
if(activeTab==="home"){
fetch(`${API_URL}/live-matches`)
.then(res=>res.json())
.then(data=>setLiveMatches(data || []))
.catch(()=>setLiveMatches([]));
}
},[activeTab]);

// ================= COMMENTARY =================
const [commentary,setCommentary]=useState(null);
const [loadingCommentary,setLoadingCommentary]=useState(false);
const intervalRef=useRef(null);

const loadCommentary=async(match)=>{
if(!match) return;

setLoadingCommentary(true);

try{
const res=await fetch(
`${API_URL}/match-commentary?team1=${match.team1}&team2=${match.team2}&status=${encodeURIComponent(match.status)}`
);
const data=await res.json();
setCommentary(data);
}catch{
setCommentary({commentary:"Error loading commentary"});
}

setLoadingCommentary(false);
};

useEffect(()=>{
if(selectedMatch){
loadCommentary(selectedMatch);

intervalRef.current=setInterval(()=>{
loadCommentary(selectedMatch);
},20000);
}

return ()=>{
if(intervalRef.current){
clearInterval(intervalRef.current);
intervalRef.current=null;
}
};
},[selectedMatch]);

// ================= VOICE =================
const startVoice=()=>{
if(!("webkitSpeechRecognition" in window)) return;

const rec=new window.webkitSpeechRecognition();
rec.lang="en-IN";
rec.continuous=true;

let final="";

rec.onstart=()=>setListening(true);

rec.onresult=(e)=>{
for(let i=e.resultIndex;i<e.results.length;i++){
let t=e.results[i][0].transcript;
if(e.results[i].isFinal) final+=t;
}
setQuestion(final);
};

rec.onend=()=>{
setListening(false);
if(final.trim()) askAI(final);
};

rec.start();
setTimeout(()=>rec.stop(),5000);
};

// ================= STATS =================
useEffect(()=>{
const i=setInterval(()=>{
setStats([...statsPool].sort(()=>0.5-Math.random()).slice(0,3));
},8000);
return ()=>clearInterval(i);
},[]);

// ================= FEED =================
useEffect(()=>{
if(activeTab==="home"){
fetch(`${API_URL}/feed`)
.then(res=>res.json())
.then(data=>setFeed(data))
.catch(()=>setFeed(null));
}
},[activeTab]);

// ================= SCROLL =================
useEffect(()=>{
chatEndRef.current?.scrollIntoView({behavior:"smooth"});
},[messages]);

// ================= ASK =================
const askAI=async(q=question)=>{
if(!q.trim()) return;

setLoading(true);

const newMsg=[...messages,{role:"user",text:q}];
setMessages(newMsg);
setQuestion("");

try{
const res=await fetch(`${API_URL}/ask?question=${encodeURIComponent(q)}`);
const data=await res.json();

const ans=data?.answer || "No response";

setMessages([...newMsg,{role:"ai",text:ans}]);
speakText(ans);

}catch{
const err="Server error";
setMessages([...newMsg,{role:"ai",text:err}]);
speakText(err);
}

setLoading(false);
};

// ================= UI =================
return(
<div className="app">

<header className="header">
<div className="brand">
<img src={logo} className="logo" alt="logo"/>
<div className="title">
<h1>SportsFan360</h1>
<p>AI Cricket Analyst</p>
</div>
</div>
</header>

<div className="tabs">
<button className={activeTab==="home"?"tab active":"tab"} onClick={()=>setActiveTab("home")}>🏠 Home</button>
<button className={activeTab==="ask"?"tab active":"tab"} onClick={()=>setActiveTab("ask")}>🤖 AskSportsFan360</button>
<button className={activeTab==="trivia"?"tab active":"tab"} onClick={()=>setActiveTab("trivia")}>🏏 IPL Trivia</button>
<button className={activeTab==="battle"?"tab active":"tab"} onClick={()=>setActiveTab("battle")}>⚔️ Player Battle</button>
</div>

{/* HOME */}
{activeTab==="home" && (
<div className="home">

<h2>🔴 Live Matches</h2>

{liveMatches.length===0 && <p>No matches available</p>}

<div className="liveMatches">
{liveMatches.map((m,i)=>(
<div key={i} className="matchCard" onClick={()=>setSelectedMatch(m)}>
<h3>{m.team1} vs {m.team2}</h3>
<p>{m.status}</p>
<span>{m.venue}</span>
</div>
))}
</div>

{selectedMatch && (
<div className="matchDetail">

<h2>{selectedMatch.team1} vs {selectedMatch.team2}</h2>
<p>{selectedMatch.status}</p>

{loadingCommentary && <p>Analyzing match...</p>}

{commentary && <p>{commentary.commentary}</p>}

<button onClick={()=>setSelectedMatch(null)}>Close</button>

</div>
)}

<h2>🔥 IPL Quick Stats</h2>
<div className="quickStats">
{stats.map((s,i)=>(
<div key={i}>{s.label} - {s.value}</div>
))}
</div>

<h2>📰 Latest News</h2>

{feed?.cards?.map((c,i)=>(
<a key={i} href={c.link} target="_blank" rel="noreferrer">
<p>{c.title}</p>
</a>
))}

</div>
)}

{/* ASK */}
{activeTab==="ask" && (
<div className="askPage">

<h2>Ask anything about IPL</h2>

<div className="chatMessages">
{messages.map((m,i)=>(
<div key={i} className={m.role}>{m.text}</div>
))}
{loading && <div>Analyzing...</div>}
<div ref={chatEndRef}></div>
</div>

<input value={question} onChange={(e)=>setQuestion(e.target.value)} />
<button onClick={askAI}>Ask</button>
<button onClick={startVoice}>{listening?"Listening...":"🎤"}</button>

</div>
)}

{activeTab==="trivia" && <Trivia />}
{activeTab==="battle" && <PlayerBattle API_URL={API_URL}/>}

</div>
);
}

export default App;