import React from "react";
import ReactDOM from "react-dom/client";
import "./index.css";
import App from "./App";
import "./output.css";

const container = document.getElementById("root") as HTMLElement;
if (container !== null) {
  const root = ReactDOM.createRoot(container);
  root.render(
    <React.StrictMode>
      <App />
    </React.StrictMode>
  );
} else {
  console.error("Failed to find the root element");
}
