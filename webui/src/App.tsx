import "./App.css";

import { ErrorBoundary } from "react-error-boundary";
import { PySimapleProvider } from "./hooks/useSimaple";
import { Router } from "./Router";

function App() {
  return (
    <ErrorBoundary
      fallbackRender={({ error }) => <div>Error: {error.message}</div>}
    >
      <PySimapleProvider>
        <Router />
      </PySimapleProvider>
    </ErrorBoundary>
  );
}

export default App;
