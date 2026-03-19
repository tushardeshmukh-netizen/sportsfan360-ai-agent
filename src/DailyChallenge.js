import React, { useState, useEffect } from "react";

function DailyChallenge({ match, API_URL }) {

  const [prediction, setPrediction] = useState(null);
  const [answers, setAnswers] = useState({});
  const [submitted, setSubmitted] = useState(false);

  const matchId = match?.id || `${match?.team1}-${match?.team2}`;

  // LOAD CHALLENGE
  useEffect(() => {
    fetch(`${API_URL}/daily-challenge?matchId=${matchId}`)
      .then(res => res.json())
      .then(data => setPrediction(data))
      .catch(() => setPrediction(null));
  }, [matchId]);

  // LOAD USER DATA
  useEffect(() => {
    const saved = localStorage.getItem("ipl_prediction");
    if (saved) {
      const parsed = JSON.parse(saved);
      if (parsed.matchId === matchId) {
        setAnswers(parsed.answers);
        setSubmitted(true);
      }
    }
  }, [matchId]);

  const handleSelect = (qId, option) => {
    if (submitted) return;
    setAnswers({ ...answers, [qId]: option });
  };

  const handleSubmit = () => {
    const data = {
      matchId,
      answers,
      submittedAt: Date.now()
    };

    localStorage.setItem("ipl_prediction", JSON.stringify(data));
    setSubmitted(true);
  };

  if (!prediction || !match) return null;

  return (
    <div className="challengeCard">

      <h3>🔥 Daily IPL Challenge</h3>
      <p>{match.team1} vs {match.team2}</p>

      {prediction.questions.map((q, i) => (
        <div key={i} className="questionBlock">

          <p>{q.question}</p>

          <div className="options">
            {q.options.map((opt, idx) => (
              <button
                key={idx}
                className={answers[q.id] === opt ? "selected" : ""}
                onClick={() => handleSelect(q.id, opt)}
              >
                {opt}
              </button>
            ))}
          </div>

        </div>
      ))}

      {!submitted ? (
        <button className="submitBtn" onClick={handleSubmit}>
          Submit Predictions
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