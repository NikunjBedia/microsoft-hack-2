import React from "react";
import ReactDOM from "react-dom/client";
import "./index.css";
import App from "./App";
import "./output.css";
import { Provider } from "react-redux";
import store from "./lib/store";

const container = document.getElementById("root") as HTMLElement;
if (container !== null) {
  const root = ReactDOM.createRoot(container);
  root.render(
    <React.StrictMode>
      <Provider store={store}>
        <App />
      </Provider>
    </React.StrictMode>
  );
} else {
  console.error("Failed to find the root element");
}
