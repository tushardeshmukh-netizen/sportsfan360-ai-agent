import React,{useState,useRef,useEffect} from "react";
import "./App.css";
import logo from "./assets/logo.png";

function App(){

const API_URL="https://sportsfan360-ai-agent-1.onrender.com"

const [question,setQuestion]=useState("")
const [messages,setMessages]=useState([])
const [loading,setLoading]=useState(false)

const chatEndRef=useRef()

const suggestions=[
"Who scored most IPL runs",
"Top wicket takers IPL",
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

const askAI=async(q=question)=>{

if(!q.trim())return

setLoading(true)

const newMessages=[...messages,{role:"user",text:q}]
setMessages(newMessages)
setQuestion("")

try{

const res=await fetch(`${API_URL}/ask?question=${encodeURIComponent(q)}`)
const data=await res.json()

let text=""

if(data.chart_data && data.chart_data.length>0){

text+=data.chart_title+"\n\n"

data.chart_data.forEach((p,i)=>{
text+=`${i+1}. ${p.player} — ${p.value}\n`
})

if(data.answer){
text+="\n"+data.answer
}

}else{
text=data.answer
}

setMessages([...newMessages,{role:"ai",text:text}])

}catch{

setMessages([...newMessages,{role:"ai",text:"Server error"}])

}

setLoading(false)

}

return(

<div className="app">

<header className="header">

<img src={logo} className="logo" alt="logo"/>

<div className="title">
<h1>SportsFan360</h1>
<p>AI Cricket Analyst</p>
</div>

<button className="clearChat" onClick={clearChat}>
Clear Chat
</button>

</header>

<div className="chatPanel">

{messages.map((m,i)=>(
<div key={i} className={`message ${m.role}`}>
<div className="messageText">{m.text}</div>
</div>
))}

{loading && (
<div className="message ai typing">
Analyzing cricket data...
</div>
)}

<div ref={chatEndRef}></div>

</div>

<div className="search">

<input
value={question}
placeholder="Ask SportsFan360 AI..."
onChange={(e)=>setQuestion(e.target.value)}
onKeyDown={(e)=>{if(e.key==="Enter")askAI()}}
/>

<button onClick={()=>askAI()}>
Ask
</button>

</div>

<div className="suggestions">

{suggestions.map((s,i)=>(
<button key={i} onClick={()=>askAI(s)}>
{s}
</button>
))}

</div>

<footer className="footer">
© {new Date().getFullYear()} SportsFan360
</footer>

</div>

)

}

export default App
