import React, { useState } from "react";
import "./App.css";
import logo from "./assets/logo.png";

import RunsChart from "./components/RunsChart";
import WicketsChart from "./components/WicketsChart";

function App() {

  const [question, setQuestion] = useState("");
  const [result, setResult] = useState(null);
  const [showJSON, setShowJSON] = useState(false);
  const [chartType, setChartType] = useState("runs");


  const askAI = async () => {

    if (!question) return;

    try {

      // LOCAL SERVER
      //const API_URL = "http://127.0.0.1:8000";

      // PRODUCTION SERVER
      const API_URL = "https://sportsfan360-ai-agent-1.onrender.com";

      const response = await fetch(
        `${API_URL}/ask?question=${encodeURIComponent(question)}`
      );

      const data = await response.json();

      console.log("API RESPONSE:", data);

      // FIX: Normalize backend responses
      if (data.top_wicket_takers && !data.chart_data) {

        data.chart_data = data.top_wicket_takers;

        data.chart_title = "Top IPL Wicket Takers";

      }

      setResult(data);

      if (data.chart_title) {

        if (data.chart_title.toLowerCase().includes("wicket")) {
          setChartType("wickets");
        } else {
          setChartType("runs");
        }

      }

    } catch (error) {

      console.error(error);

      setResult({
        answer: "Server error. Check backend."
      });

    }

  };


  const clearSearch = () => {

    setQuestion("");
    setResult(null);
    setShowJSON(false);

  };


  const renderResult = () => {

    if (!result) return null;


    if (result.winner) {

      return (
        <div className="card">

          <h3>🏆 IPL {result.season} Winner</h3>
          <p className="big">{result.winner}</p>

        </div>
      );

    }


    if (result.chart_data) {

      return (

        <div className="card">

          <h3>{result.chart_title}</h3>

          {result.chart_data.map((p, i) => (

            <p key={i}>
              {i + 1}. {p.player} — {p.value}
            </p>

          ))}

          {result.answer && (
            <p className="insight">💡 {result.answer}</p>
          )}

        </div>

      );

    }


    if (result.answer) {

      return (

        <div className="card">

          {result.chart_title && <h3>{result.chart_title}</h3>}

          <p>{result.answer}</p>

        </div>

      );

    }

    return <p>No result</p>;

  };


  const chartData =
    result?.chart_data ||
    result?.top_wicket_takers ||
    [];


  return (

    <div className="app">

      <header className="header">

        <img src={logo} className="logo" alt="logo" />

        <div className="title">

          <h1>SportsFan360</h1>
          <p>AI IPL Analytics Dashboard</p>

        </div>

      </header>


      <div className="search">

        <input
          placeholder="Ask anything about IPL..."
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter") askAI();
          }}
        />

        <button onClick={askAI}>
          Ask
        </button>

        <button onClick={clearSearch} className="clearBtn">
          Clear
        </button>

      </div>


      {result && (

        <div className="result">

          <h2>Result</h2>

          {renderResult()}

          <div className="jsonToggle">

            <button onClick={() => setShowJSON(!showJSON)}>
              {showJSON ? "Hide JSON" : "Show JSON"}
            </button>

            {showJSON && (

              <pre>
                {JSON.stringify(result, null, 2)}
              </pre>

            )}

          </div>

        </div>

      )}


      <div className="examples">

        <p>Try asking:</p>

        <ul>
          <li>Who won IPL 2022</li>
          <li>Which team has most IPL titles</li>
          <li>Top run scorers</li>
          <li>Most wickets</li>
          <li>Highest score</li>
          <li>Compare Kohli vs Rohit IPL runs</li>
        </ul>

      </div>


      {chartData.length > 0 && (

        <div className="analytics">

          <h2>{result.chart_title || "Match Analytics"}</h2>

          <div className="chartBox">

            {chartType === "runs" && (
              <RunsChart data={chartData} />
            )}

            {chartType === "wickets" && (
              <WicketsChart data={chartData} />
            )}

          </div>

        </div>

      )}

    </div>

  );

}

export default App;