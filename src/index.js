import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App";

const root = ReactDOM.createRoot(document.getElementById("root"));

try {
  root.render(
    <React.StrictMode>
      <App />
    </React.StrictMode>
  );
} catch (e) {
  console.error("ROOT CRASH:", e);

  document.body.innerHTML = `
    <div style="padding:20px;color:red">
      App crashed. Check console.
    </div>
  `;
}