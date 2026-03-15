import React, { useState, useRef, useEffect } from "react";
import "./App.css";
import logo from "./assets/logo.png";

import RunsChart from "./components/RunsChart";
import WicketsChart from "./components/WicketsChart";

function App() {

  /* ===============================
     API SERVER TOGGLE
     =============================== */

  // ===== LOCAL SERVER =====
  //const API_URL = "http://127.0.0.1:8000";

  // ===== PRODUCTION SERVER (Render) =====
   const API_URL = "https://sportsfan360-ai-agent-1.onrender.com";


  const SHOW_CHARTS = false;   // charts hidden for now

  const [question, setQuestion] = useState("");
  const [messages, setMessages] = useState([]);
  const [chartData, setChartData] = useState([]);
  const [chartTitle, setChartTitle] = useState("");
  const [chartType, setChartType] = useState("runs");
  const [loading, setLoading] = useState(false);

  const chatEndRef = useRef();

  const suggestions = [
    "Who has most IPL runs",
    "Top wicket takers IPL",
    "Which team has most IPL titles",
    "Highest IPL score",
    "Compare Kohli vs Rohit IPL runs",
    "Why is IPL popular"
  ];

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);


  /* ===============================
     CLEAR CHAT
     =============================== */

  const clearChat = () => {
    setMessages([]);
    setChartData([]);
    setChartTitle("");
  };


  /* ===============================
     FORMAT ANSWERS
     =============================== */

  const formatAnswer = (data, question) => {

    let text = "";

    if (question.toLowerCase().includes("compare") && data.chart_data?.length >= 2) {

      const p1 = data.chart_data[0];
      const p2 = data.chart_data[1];

      text += `Comparison: ${p1.player} vs ${p2.player}\n\n`;

      text += `${p1.player} — ${p1.value} runs\n`;
      text += `${p2.player} — ${p2.value} runs\n\n`;

      if (p1.value > p2.value) {
        text += `${p1.player} leads by ${p1.value - p2.value} runs in IPL history.`;
      } else {
        text += `${p2.player} leads by ${p2.value - p1.value} runs in IPL history.`;
      }

      return text;
    }

    if (data.chart_data && data.chart_data.length > 0) {

      text += data.chart_title + "\n\n";

      data.chart_data.slice(0,10).forEach((p, i) => {
        text += `${i+1}. ${p.player} — ${p.value}\n`;
      });

      if (data.answer) {
        text += `\n${data.answer}`;
      }

      return text;
    }

    return data.answer || "No answer available.";
  };


  /* ===============================
     ASK AI
     =============================== */

  const askAI = async (q = question) => {

    if (!q.trim()) return;

    setLoading(true);

    const newMessages = [
      ...messages,
      { role: "user", text: q }
    ];

    setMessages(newMessages);
    setQuestion("");

    try {

      const response = await fetch(
        `${API_URL}/ask?question=${encodeURIComponent(q)}`
      );

      const data = await response.json();

      console.log("API RESPONSE:", data);

      const answerText = formatAnswer(data, q);

      setMessages([
        ...newMessages,
        { role: "ai", text: answerText }
      ]);

      if (data.chart_data) {

        setChartData(data.chart_data);
        setChartTitle(data.chart_title);

        if (data.chart_title?.toLowerCase().includes("wicket")) {
          setChartType("wickets");
        } else {
          setChartType("runs");
        }

      }

    } catch (error) {

      setMessages([
        ...newMessages,
        { role: "ai", text: "Server error. Unable to reach AI agent." }
      ]);

    }

    setLoading(false);

  };


  /* ===============================
     UI
     =============================== */

  return (

    <div className="app">

      {/* HEADER */}

      <header className="header">

        <img src={logo} className="logo" alt="logo"/>

        <div className="title">
          <h1>SportsFan360</h1>
          <p>AI Cricket Analyst</p>
        </div>

        <button className="clearChat" onClick={clearChat}>
          Clear
        </button>

      </header>


      {/* CHAT PANEL */}

      <div className="chatPanel">

        {messages.map((m,i)=>(
          <div key={i} className={`message ${m.role}`}>
            <pre>{m.text}</pre>
          </div>
        ))}

        {loading && (
          <div className="message ai">
            AI is analyzing IPL statistics...
          </div>
        )}

        <div ref={chatEndRef}></div>

      </div>


      {/* SEARCH */}

      <div className="search">

        <input
          value={question}
          placeholder="Ask the AI cricket analyst..."
          onChange={(e)=>setQuestion(e.target.value)}
          onKeyDown={(e)=>{
            if(e.key==="Enter") askAI();
          }}
        />

        <button onClick={()=>askAI()}>
          Ask
        </button>

      </div>


      {/* SUGGESTIONS */}

      <div className="suggestions">

        {suggestions.map((s,i)=>(
          <button key={i} onClick={()=>askAI(s)}>
            {s}
          </button>
        ))}

      </div>


      {/* CHARTS (hidden but not removed) */}

      {SHOW_CHARTS && chartData.length>0 && (

        <div className="analytics">

          <h2>{chartTitle}</h2>

          <div className="chartBox">

            {chartType==="runs" && (
              <RunsChart data={chartData}/>
            )}

            {chartType==="wickets" && (
              <WicketsChart data={chartData}/>
            )}

          </div>

        </div>

      )}

    </div>

  );

}

export default App;
