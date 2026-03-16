import React,{useState,useRef,useEffect} from "react";
import "./App.css";
import logo from "./assets/logo.png";


/* EXPANDED QUICK STATS */

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

/* FEED DEFAULT */

const [activeTab,setActiveTab]=useState("feed")

const [feed,setFeed]=useState(null)

const [question,setQuestion]=useState("")
const [messages,setMessages]=useState([])
const [loading,setLoading]=useState(false)

const chatEndRef=useRef()

const [stats,setStats]=useState(statsPool.slice(0,3))


/* ROTATING QUICK STATS */

useEffect(()=>{

const interval=setInterval(()=>{

const shuffled=[...statsPool].sort(()=>0.5-Math.random())
setStats(shuffled.slice(0,3))

},8000)

return ()=>clearInterval(interval)

},[])


/* LOAD FEED */

useEffect(()=>{

if(activeTab==="feed"){

fetch(`${API_URL}/feed`)
.then(res=>res.json())
.then(data=>setFeed(data))
.catch(()=>setFeed(null))

}

},[activeTab])


const suggestions=[
"Most IPL runs",
"Most IPL wickets",
"Most IPL sixes",
"Which team has most IPL titles",
"Highest IPL score",
"Compare Kohli vs Rohit",
"Why is IPL popular"
]


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
text:data.answer,
data:data
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


{/* TABS */}

<div className="tabs">

<button
className={activeTab==="feed"?"tab active":"tab"}
onClick={()=>setActiveTab("feed")}
>
Feed
</button>

<button
className={activeTab==="ask"?"tab active":"tab"}
onClick={()=>setActiveTab("ask")}
>
AskSportsFan360
</button>

</div>


{/* FEED TAB */}

{activeTab==="feed" && (

<div className="feed">

<h2>Sports Insights</h2>

{!feed && <p>Loading feed...</p>}

{feed && (

<div className="feedCards">

{feed.cards.map((c,i)=>(

<div key={i} className="feedCard">

<h3>{c.title}</h3>

<p>{c.text}</p>

{c.type==="question" && (

<button
onClick={()=>{
setActiveTab("ask")
askAI(c.text)
}}
>
Ask this →
</button>

)}

</div>

))}

</div>

)}

</div>

)}


{/* ASK TAB */}

{activeTab==="ask" && (

<>

{/* CLEAR CHAT BUTTON MOVED HERE */}

<div style={{display:"flex",justifyContent:"flex-end",marginBottom:"10px"}}>

<button className="clearChat" onClick={clearChat}>
Clear Chat
</button>

</div>


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


<main className="chatPanel">

{messages.length===0 && (
<div className="welcome">
<h2>Ask anything about IPL</h2>
<p>Runs • Wickets • Records • Comparisons</p>
</div>
)}

{messages.map((m,i)=>(
<div key={i} className={`message ${m.role}`}>

<div className="messageText">{m.text}</div>

{m.data?.chart_data?.length>0 && (

<div className="chart">

{m.data.chart_data.map((p,j)=>(
<div key={j} className="chartRow">

<span className="player">{p.player}</span>

<div className="barWrap">
<div
className="bar"
style={{width:(p.value/300)*100+"%"}}
></div>
</div>

<span className="value">{p.value}</span>

</div>
))}

</div>

)}

</div>
))}

{loading && <div className="message ai typing">Analyzing IPL data...</div>}

<div ref={chatEndRef}></div>

</main>


<div className="bottomPanel">

<div className="suggestions">

{suggestions.map((s,i)=>(
<button key={i} onClick={()=>askAI(s)}>
{s}
</button>
))}

</div>

<div className="inputBox">

<input
value={question}
placeholder="Ask SportsFan360..."
onChange={(e)=>setQuestion(e.target.value)}
onKeyDown={(e)=>{if(e.key==="Enter")askAI()}}
/>

<button onClick={()=>askAI()}>
Ask
</button>

</div>

</div>

</>

)}

</div>

)

}

export default App