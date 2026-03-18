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

// ================= VOICE =================
const isVoiceSupported = typeof window !== "undefined" && "webkitSpeechRecognition" in window;
const isSpeechOutputSupported = typeof window !== "undefined" && "speechSynthesis" in window;

const speakText=(text)=>{
  if(!isSpeechOutputSupported) return;
  window.speechSynthesis.cancel();
  const utterance=new SpeechSynthesisUtterance(text);
  utterance.lang="en-IN";
  utterance.onstart=()=>setSpeaking(true);
  utterance.onend=()=>setSpeaking(false);
  window.speechSynthesis.speak(utterance);
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
const commentaryIntervalRef = useRef(null);

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

    commentaryIntervalRef.current=setInterval(()=>{
      loadCommentary(selectedMatch);
    },20000);
  }

  return ()=>{
    if(commentaryIntervalRef.current){
      clearInterval(commentaryIntervalRef.current);
      commentaryIntervalRef.current=null;
    }
  };

},[selectedMatch]);

// ================= VOICE INPUT =================
const startVoice=()=>{
  if(!isVoiceSupported) return;

  const SpeechRecognition=window.webkitSpeechRecognition;
  const recognition=new SpeechRecognition();

  recognition.lang="en-IN";
  recognition.continuous=true;
  recognition.interimResults=true;

  let finalTranscript="";

  recognition.onstart=()=>setListening(true);

  recognition.onresult=(e)=>{
    let interim="";
    for(let i=e.resultIndex;i<e.results.length;i++){
      let transcript=e.results[i][0].transcript;
      if(e.results[i].isFinal){
        finalTranscript+=transcript;
      }else{
        interim+=transcript;
      }
    }
    setQuestion(finalTranscript + interim);
  };

  recognition.onend=()=>{
    setListening(false);
    if(finalTranscript.trim()){
      askAI(finalTranscript);
    }
  };

  recognition.onerror=()=>setListening(false);

  recognition.start();
  setTimeout(()=>recognition.stop(),6000);
};

// ================= STATS =================
useEffect(()=>{
  const interval=setInterval(()=>{
    const shuffled=[...statsPool].sort(()=>0.5-Math.random());
    setStats(shuffled.slice(0,3));
  },8000);
  return ()=>clearInterval(interval);
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

const clearChat=()=>setMessages([]);

// ================= ASK =================
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
    const errorMsg="Server error";
    setMessages([...newMessages,{role:"ai",text:errorMsg}]);
    speakText(errorMsg);
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

{/* ================= HOME ================= */}
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

{commentary && (
<>
<p>{commentary.commentary}</p>
</>
)}

<button onClick={()=>{
setSelectedMatch(null);
setCommentary(null);
}}>
Close
</button>

</div>
)}

<h2>🔥 IPL Quick Stats</h2>
<div className="quickStats">
{stats.map((s,i)=>(
<div key={i}>{s.label} - {s.value}</div>
))}
</div>

<h2>📰 Latest News</h2>

{feed?.cards?.length>0 ? (
<div className="feedCards">
{feed.cards.map((c,i)=>(
<a key={i} href={c.link} target="_blank" rel="noreferrer">
<p>{c.title}</p>
</a>
))}
</div>
):(
<p>No news available</p>
)}

</div>
)}

{/* ================= ASK ================= */}
{activeTab==="ask" && (
<div className="askPage">

<h2>Ask anything about IPL</h2>

<div className="chatMessages">

{messages.map((m,i)=>(
<div key={i}>{m.text}</div>
))}

{loading && <div>Analyzing...</div>}

<div ref={chatEndRef}></div>

</div>

<input
value={question}
placeholder={listening ? "Listening..." : "Ask SportsFan360..."}
onChange={(e)=>setQuestion(e.target.value)}
onKeyDown={(e)=>{if(e.key==="Enter")askAI()}}
/>

<button onClick={askAI}>Ask</button>

</div>
)}

{activeTab==="trivia" && <Trivia />}
{activeTab==="battle" && <PlayerBattle API_URL={API_URL}/>}

</div>
);
}

export default App;