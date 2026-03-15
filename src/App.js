import React,{useState,useRef,useEffect} from "react";
import "./App.css";
import logo from "./assets/logo.png";

function App(){

const API_URL="https://sportsfan360-ai-agent-1.onrender.com"

const [question,setQuestion]=useState("")
const [messages,setMessages]=useState([])
const [loading,setLoading]=useState(false)
const [showJSON,setShowJSON]=useState(false)

const chatEndRef=useRef()

const suggestions=[
"Most IPL runs",
"Most IPL wickets",
"Most IPL sixes",
"Which team has most IPL titles",
"Highest IPL score"
]

useEffect(()=>{
chatEndRef.current?.scrollIntoView({behavior:"smooth"})
},[messages])

const askAI=async(q=question)=>{

if(!q.trim()) return

setLoading(true)

const newMessages=[...messages,{role:"user",text:q}]
setMessages(newMessages)
setQuestion("")

try{

const res=await fetch(`${API_URL}/ask?question=${encodeURIComponent(q)}`)
const data=await res.json()

setMessages([...newMessages,{role:"ai",text:data.answer,data:data}])

}catch{

setMessages([...newMessages,{role:"ai",text:"Server error"}])

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

<main className="chatPanel">

{messages.length===0 && (
<div className="welcome">
<h2>Ask anything about IPL</h2>
</div>
)}

{messages.map((m,i)=>(
<div key={i} className={`message ${m.role}`}>

<div>{m.text}</div>

{m.data?.chart_data?.length>0 && (

<div className="chart">

{m.data.chart_data.map((p,j)=>(
<div key={j} className="chartRow">
<span>{p.player}</span>
<div className="bar" style={{width:(p.value/100)*20+"%"}}></div>
<span>{p.value}</span>
</div>
))}

</div>

)}

</div>
))}

{loading && <div className="message ai">Analyzing IPL data...</div>}

<div ref={chatEndRef}></div>

</main>

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

)

}

export default App
