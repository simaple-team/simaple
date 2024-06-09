import "./App.css";
import Header from "./components/Header";
import { PreferenceProvider } from "./hooks/usePreference";
import { WorkspaceProvider } from "./hooks/useWorkspace";
import Editor from "./pages/Editor";

function App() {
  return (
    <WorkspaceProvider>
      <PreferenceProvider>
        <div className="h-screen flex flex-col">
          <Header />
          <Editor />
        </div>
      </PreferenceProvider>
    </WorkspaceProvider>
  );
}

export default App;
