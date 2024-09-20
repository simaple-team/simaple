import { Editor } from "@/components/Editor";
import Header from "@/components/Header";
import { PreferenceProvider } from "@/hooks/usePreference";
import { usePySimapleBeforeLoad } from "@/hooks/useSimaple";
import { WorkspaceProvider } from "@/hooks/useWorkspaceState";
import { Navigate, NavLink, Outlet } from "react-router-dom";

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
            <div className="flex grow flex-col">
              <div className="h-12 border-b border-border/40 bg-background shrink-0">
                <div className="flex h-full gap-4 px-4">
                  <NavLink
                    to="/editor/summary"
                    className={({ isActive }) =>
                      isActive
                        ? "flex items-center justify-center px-4 text-center text-sm transition-colors hover:text-primary font-semibold text-primary border-b-2 border-b-primary"
                        : "flex items-center justify-center px-4 text-center text-sm transition-colors hover:text-primary text-muted-foreground border-b-2 border-b-transparent"
                    }
                  >
                    전투분석
                  </NavLink>
                  <NavLink
                    to="/editor/log"
                    className={({ isActive }) =>
                      isActive
                        ? "flex items-center justify-center px-4 text-center text-sm transition-colors hover:text-primary font-semibold text-primary border-b-2 border-b-primary"
                        : "flex items-center justify-center px-4 text-center text-sm transition-colors hover:text-primary text-muted-foreground border-b-2 border-b-transparent"
                    }
                  >
                    로그
                  </NavLink>
                  <NavLink
                    to="/editor/chart"
                    className={({ isActive }) =>
                      isActive
                        ? "flex items-center justify-center px-4 text-center text-sm transition-colors hover:text-primary font-semibold text-primary border-b-2 border-b-primary"
                        : "flex items-center justify-center px-4 text-center text-sm transition-colors hover:text-primary text-muted-foreground border-b-2 border-b-transparent"
                    }
                  >
                    차트
                  </NavLink>
                </div>
              </div>
              <Outlet />
            </div>
          </div>
        </div>
      </PreferenceProvider>
    </WorkspaceProvider>
  );
}
