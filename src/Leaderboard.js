import React, { useEffect, useState } from "react";

function Leaderboard() {

  const [leaders, setLeaders] = useState([]);

  useEffect(() => {

    const data = localStorage.getItem("ipl_leaderboard");

    if (data) {
      setLeaders(JSON.parse(data));
    } else {
      // 🔥 Default demo leaderboard
      const demo = [
        { name: "You", score: 50 },
        { name: "Player123", score: 40 },
        { name: "CricketFan", score: 30 }
      ];
      localStorage.setItem("ipl_leaderboard", JSON.stringify(demo));
      setLeaders(demo);
    }

  }, []);

  return (
    <div className="leaderboardCard">

      <h3>🏆 Leaderboard</h3>

      {leaders.map((l, i) => (
        <div key={i} className={`leaderRow ${l.name === "You" ? "you" : ""}`}>

          <span className="rank">#{i + 1}</span>
          <span className="name">{l.name}</span>
          <span className="score">{l.score} pts</span>

        </div>
      ))}

    </div>
  );
}

export default Leaderboard;