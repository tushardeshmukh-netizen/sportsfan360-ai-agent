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
{label:"Fastest IPL Century",value:"Chris Gayle",num:"30 balls"}
];

function App(){

const API_URL="https://sportsfan360-ai-agent-1.onrender.com";

const [activeTab,setActiveTab]=useState("home");
const [feed,setFeed]=useState(null);
const [liveMatches,setLiveMatches]=useState([]);
const [selectedMatch,setSelectedMatch]=useState(null);

const [question,setQuestion]=useState("");
const [messages,setMessages]=useState([]);
const [loading,setLoading]=useState(false);

const chatEndRef=useRef();
const [stats,setStats]=useState(statsPool.slice(0,3));

const [speaking,setSpeaking]=useState(false);
const [listening,setListening]=useState(false);

// ================= VOICE SUPPORT =================
const isVoiceSupported = typeof window !== "undefined" && "webkitSpeechRecognition" in window;
const isSpeechOutputSupported = typeof window !== "undefined" && "speechSynthesis" in window;

// ================= SPEAK =================
const speakText=(text)=>{
if(!isSpeechOutputSupported) return;

window.speechSynthesis.cancel();

const utterance=new SpeechSynthesisUtterance(text);
utterance.lang="en-IN";

utterance.onstart=()=>setSpeaking(true);
utterance.onend=()=>setSpeaking(false);

window.speechSynthesis.speak(utterance);
};

// ================= VOICE INPUT =================
const startVoice=()=>{
if(!isVoiceSupported) return;

const SpeechRecognition=window.webkitSpeechRecognition;
const recognition=new SpeechRecognition();

recognition.lang="en-IN";
recognition.continuous=false;
recognition.interimResults=false;

recognition.onstart=()=>setListening(true);

recognition.onresult=(e)=>{
const transcript=e.results[0][0].transcript;
setQuestion(transcript);
askAI(transcript);
};

recognition.onend=()=>setListening(false);
recognition.onerror=()=>setListening(false);

recognition.start();
};

// ================= LOAD DATA =================
useEffect(()=>{
if(activeTab==="home"){

fetch(`${API_URL}/live-matches`)
.then(res=>res.json())
.then(data=>{
if(data && data.length>0){
setLiveMatches(data);
}else{
setLiveMatches([
{team1:"CSK",team2:"MI",status:"Upcoming",venue:"Wankhede Stadium"},
{team1:"RCB",team2:"KKR",status:"Upcoming",venue:"Chinnaswamy"}
]);
}
})
.catch(()=>setLiveMatches([]));

fetch(`${API_URL}/feed`)
.then(res=>res.json())
.then(data=>setFeed(data))
.catch(()=>setFeed(null));

}
},[activeTab]);

// ================= STATS =================
useEffect(()=>{
const interval=setInterval(()=>{
setStats([...statsPool].sort(()=>0.5-Math.random()).slice(0,3));
},5000);
return ()=>clearInterval(interval);
},[]);

// ================= SCROLL =================
useEffect(()=>{
chatEndRef.current?.scrollIntoView({behavior:"smooth"});
},[messages]);

// ================= ASK AI =================
const askAI=async(q=question)=>{
if(!q.trim()) return;

setLoading(true);

const newMessages=[...messages,{role:"user",text:q}];
setMessages(newMessages);
setQuestion("");

try{
const res=await fetch(`${API_URL}/ask?question=${encodeURIComponent(q)}`);
const data=await res.json();

const answer=data?.answer || "No response";

setMessages([...newMessages,{role:"ai",text:answer}]);
speakText(answer);

}catch{
setMessages([...newMessages,{role:"ai",text:"Server error"}]);
}

setLoading(false);
};

// ================= UI =================
return(
<div className="app">

<header className="header">
<div className="brand">
<img src={logo} className="logo" alt="logo"/>
<div>
<h1>SportsFan360</h1>
<p>AI Cricket Analyst</p>
</div>
</div>
</header>

<div className="tabs">
<button className={activeTab==="home"?"tab active":"tab"} onClick={()=>setActiveTab("home")}>🏠 Home</button>
<button className={activeTab==="ask"?"tab active":"tab"} onClick={()=>setActiveTab("ask")}>🤖 AskSportsFan360</button>
<button className={activeTab==="trivia"?"tab active":"tab"} onClick={()=>setActiveTab("trivia")}>🏏 Trivia</button>
<button className={activeTab==="battle"?"tab active":"tab"} onClick={()=>setActiveTab("battle")}>⚔️ Battle</button>
</div>

{/* HOME */}
{activeTab==="home" && (
<div className="home">

<h2>🔴 Live Matches</h2>

<div className="liveMatches">
{liveMatches.map((m,i)=>(
<div key={i} className="matchCard" onClick={()=>setSelectedMatch(m)}>
<h3>{m.team1} vs {m.team2}</h3>
<p>{m.status}</p>
<span>{m.venue}</span>
</div>
))}
</div>

<h2>🔥 IPL Quick Stats</h2>
<div className="statsGrid">
{stats.map((s,i)=>(
<div key={i} className="statCard">
<p>{s.label}</p>
<strong>{s.value}</strong>
<span>{s.num}</span>
</div>
))}
</div>

<h2>📰 Latest News</h2>
<div className="newsGrid">
{feed?.cards?.map((c,i)=>(
<a key={i} href={c.link} target="_blank" rel="noreferrer" className="newsCard">
<h4>{c.title}</h4>
<p>{c.text}</p>
</a>
))}
</div>

</div>
)}

{/* ASK */}
{activeTab==="ask" && (
<div className="askPage">

<h2>Ask anything about IPL</h2>

<div className="chatBox">

{messages.length===0 && (
<div style={{opacity:0.6}}>Try: "Most IPL runs"</div>
)}

{messages.map((m,i)=>(
<div key={i} className={`bubble ${m.role}`}>
{m.text}
</div>
))}

{loading && <div className="bubble ai">Analyzing...</div>}

<div ref={chatEndRef}></div>

</div>

<div className="inputBar">
<input
value={question}
placeholder={listening ? "Listening..." : "Ask SportsFan360..."}
onChange={(e)=>setQuestion(e.target.value)}
onKeyDown={(e)=>{if(e.key==="Enter")askAI()}}
/>

<button onClick={askAI}>Ask</button>
<button onClick={startVoice}>🎤</button>
</div>

</div>
)}

{activeTab==="trivia" && <Trivia />}
{activeTab==="battle" && <PlayerBattle API_URL={API_URL}/>}

</div>
);
}

export default App;