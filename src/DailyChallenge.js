import React, { useState, useEffect } from "react";

function DailyChallenge({ match, API_URL }) {

  const [prediction, setPrediction] = useState(null);
  const [answers, setAnswers] = useState({});
  const [submitted, setSubmitted] = useState(false);
  const [loading, setLoading] = useState(true);

  const matchId = match?.id || `${match?.team1}-${match?.team2}`;

  // ---------------- LOAD CHALLENGE ----------------
  useEffect(() => {

    if (!matchId) return;

    setLoading(true);

    fetch(`${API_URL}/daily-challenge?matchId=${matchId}`)
      .then(res => res.json())
      .then(data => {
        setPrediction(data);
        setLoading(false);
      })
      .catch(() => {
        setPrediction(null);
        setLoading(false);
      });

  }, [matchId, API_URL]);


  // ---------------- LOAD USER DATA ----------------
  useEffect(() => {

    const saved = localStorage.getItem("ipl_prediction");

    if (saved) {
      try {
        const parsed = JSON.parse(saved);

        if (parsed.matchId === matchId) {
          setAnswers(parsed.answers || {});
          setSubmitted(true);
        }
      } catch (e) {
        console.log("LocalStorage parse error");
      }
    }

  }, [matchId]);


  // ---------------- HANDLE SELECT ----------------
  const handleSelect = (qId, option) => {

    if (submitted) return;

    setAnswers(prev => ({
      ...prev,
      [qId]: option
    }));
  };


  // ---------------- HANDLE SUBMIT ----------------
  const handleSubmit = () => {

    if (prediction && Object.keys(answers).length !== prediction.questions.length) {
      alert("Please answer all questions ⚠️");
      return;
    }

    const data = {
      matchId,
      answers,
      submittedAt: Date.now()
    };

    localStorage.setItem("ipl_prediction", JSON.stringify(data));

    // 🔥 UPDATE LEADERBOARD
    let leaderboard = JSON.parse(localStorage.getItem("ipl_leaderboard")) || [];

    let user = leaderboard.find(l => l.name === "You");

    if (user) {
      user.score += 10;
    } else {
      leaderboard.push({ name: "You", score: 10 });
    }

    leaderboard.sort((a, b) => b.score - a.score);

    localStorage.setItem("ipl_leaderboard", JSON.stringify(leaderboard));

    setSubmitted(true);
  };


  // ---------------- LOADING STATE ----------------
  if (loading) {
    return (
      <div className="challengeCard">
        <p>Loading Daily Challenge...</p>
      </div>
    );
  }

  if (!prediction || !match) return null;


  // ---------------- UI ----------------
  return (
    <div className="challengeCard">

      <h3>🔥 Daily IPL Challenge</h3>
      <p className="matchTitle">
        {match.team1} <span>vs</span> {match.team2}
      </p>

      {prediction.questions.map((q) => (
        <div key={q.id} className="questionBlock">

          <p className="questionText">{q.question}</p>

          <div className="options">
            {q.options.map((opt, idx) => {

              const isSelected = answers[q.id] === opt;

              return (
                <button
                  key={idx}
                  className={`optionBtn ${isSelected ? "selected" : ""} ${submitted ? "locked" : ""}`}
                  onClick={() => handleSelect(q.id, opt)}
                  disabled={submitted}
                >
                  {opt}
                </button>
              );
            })}
          </div>

        </div>
      ))}

      {!submitted ? (
        <button className="submitBtn" onClick={handleSubmit}>
          Submit Predictions 🚀
        </button>
      ) : (
        <div className="submittedMsg">
          ✅ Predictions Submitted
        </div>
      )}

    </div>
  );
}

export default DailyChallenge;