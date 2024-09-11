import "./App.css";
import { PySimapleProvider } from "./hooks/useSimaple";
import { Router } from "./Router";

function App() {
  return (
    <PySimapleProvider>
      <Router />
    </PySimapleProvider>
  );
}

export default App;
