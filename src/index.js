import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App";

const root = ReactDOM.createRoot(document.getElementById("root"));

window.onerror = function (msg, url, line, col, error) {
  console.error("GLOBAL ERROR:", msg, error);
  document.body.innerHTML = `<div style="color:red;padding:20px">
    Crash Detected:<br>${msg}
  </div>`;
};

import { BrowserRouter } from "react-router-dom";

<BrowserRouter>
  <App />
</BrowserRouter>


root.render(<App />);