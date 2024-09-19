import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App.tsx";
import "./index.css";
import { PySimapleProvider } from "./hooks/useSimaple.tsx";

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <PySimapleProvider>
      <App />
    </PySimapleProvider>
  </React.StrictMode>,
);
