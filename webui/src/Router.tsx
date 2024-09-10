import Header from "./components/Header";
import { PreferenceProvider } from "./hooks/usePreference";
import { usePySimapleBeforeLoad } from "./hooks/useSimaple";
import { WorkspaceProvider } from "./hooks/useWorkspace";
import Editor from "./pages/Editor";
import { PrepareSimaple } from "./pages/PrepareSimaple";

export function Router() {
  const { isLoaded } = usePySimapleBeforeLoad();

  if (!isLoaded) {
    return <PrepareSimaple />;
  }

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
