import React,{useState,useRef,useEffect} from "react";
import "./App.css";
import logo from "./assets/logo.png";
import Trivia from "./Trivia";
// PlayerBattle disabled

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

]

function App(){

const API_URL="https://sportsfan360-ai-agent-1.onrender.com"

const [activeTab,setActiveTab]=useState("home")
const [question,setQuestion]=useState("")
const [messages,setMessages]=useState([])
const [loading,setLoading]=useState(false)

const chatEndRef=useRef()

const [stats,setStats]=useState(statsPool.slice(0,3))

/* ROTATING STATS */
useEffect(()=>{
const interval=setInterval(()=>{
const shuffled=[...statsPool].sort(()=>0.5-Math.random())
setStats(shuffled.slice(0,3))
},8000)
return ()=>clearInterval(interval)
},[])

useEffect(()=>{
chatEndRef.current?.scrollIntoView({behavior:"smooth"})
},[messages])

const clearChat=()=>{
setMessages([])
}

/* ASK AI */
const askAI=async(q=question)=>{

if(!q.trim()) return

setLoading(true)

const newMessages=[...messages,{role:"user",text:q}]
setMessages(newMessages)
setQuestion("")

try{
const res=await fetch(`${API_URL}/ask?question=${encodeURIComponent(q)}`)
const data=await res.json()

setMessages([...newMessages,{
role:"ai",
text:data?.answer || "No response"
}])

}catch{
setMessages([...newMessages,{
role:"ai",
text:"Server error"
}])
}

setLoading(false)
}

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

<button className={activeTab==="home"?"tab active":"tab"} onClick={()=>setActiveTab("home")}>
🏠 Home
</button>

<button className={activeTab==="ask"?"tab active":"tab"} onClick={()=>setActiveTab("ask")}>
🤖 AskSportsFan360
</button>

<button className={activeTab==="trivia"?"tab active":"tab"} onClick={()=>setActiveTab("trivia")}>
🏏 IPL Trivia
</button>

<button className={activeTab==="battle"?"tab active":"tab"} onClick={()=>setActiveTab("battle")}>
⚔️ Player Battle
</button>

</div>

{/* HOME */}
{activeTab==="home" && (

<div className="home">

<div className="hero">
<h2>Cricket Intelligence Hub</h2>
<p>Live insights, player trends, match analysis and AI powered cricket knowledge.</p>
</div>

<div className="sectionTitle">🔥 IPL Quick Stats</div>

<div className="quickStats">
{stats.map((s,i)=>(
<div key={i} className="statCard">
<span className="statLabel">{s.label}</span>
<div className="statRow">
<strong>{s.value}</strong>
<span className="statNum">{s.num}</span>
</div>
</div>
))}
</div>

</div>

)}

{/* ASK */}
{activeTab==="ask" && (

<div className="askPage">

<button className="clearChat" onClick={clearChat}>
Clear Chat
</button>

<main className="chatPanel">

{messages.length===0 && (
<div className="welcome">
<h2>Ask anything about IPL</h2>
</div>
)}

{messages.map((m,i)=>(
<div key={i} className={`message ${m.role}`}>
<div className="messageText">{m.text}</div>
</div>
))}

{loading && <div className="message ai">Analyzing...</div>}

<div ref={chatEndRef}></div>

</main>

<div className="inputBox">

<input
value={question}
placeholder="Ask..."
onChange={(e)=>setQuestion(e.target.value)}
onKeyDown={(e)=>{if(e.key==="Enter")askAI()}}
/>

<button onClick={()=>askAI()}>
Ask
</button>

</div>

</div>

)}

{/* TRIVIA */}
{activeTab==="trivia" && <Trivia />}

{/* BATTLE DISABLED */}
{activeTab==="battle" && (
<div style={{padding:"20px"}}>
⚠️ Player Battle disabled
</div>
)}

</div>

)

}

export default App;