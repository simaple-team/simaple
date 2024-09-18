import { Editor } from "@/components/Editor";
import Header from "@/components/Header";
import { PreferenceProvider } from "@/hooks/usePreference";
import { usePySimapleBeforeLoad } from "@/hooks/useSimaple";
import { WorkspaceProvider } from "@/hooks/useWorkspaceState";
import { Navigate, Outlet } from "react-router-dom";

export function EditorLayout() {
  const { isLoaded } = usePySimapleBeforeLoad();

  if (!isLoaded) {
    return <Navigate to="/" replace={true} />;
  }

  return (
    <WorkspaceProvider>
      <PreferenceProvider>
        <div className="h-screen flex flex-col">
          <Header />
          <div className="flex h-[calc(100vh-4rem)]">
            <Editor />
            <Outlet />
          </div>
        </div>
      </PreferenceProvider>
    </WorkspaceProvider>
  );
}
