import { Editor } from "@/components/Editor";
import Header from "@/components/Header";
import { PreferenceProvider } from "@/hooks/usePreference";
import { usePySimapleBeforeLoad } from "@/hooks/useSimaple";
import { SkillDataProvider } from "@/hooks/useSkillData";
import { WorkspaceProvider } from "@/hooks/useWorkspaceState";
import { Navigate, NavLink, Outlet } from "react-router-dom";
import { PreferencePopover } from "./PreferencePopover";
import { Settings } from "lucide-react";

const Tab = ({ to, children }: { to: string; children: React.ReactNode }) => {
  return (
    <NavLink
      to={to}
      className={({ isActive }) =>
        isActive
          ? "flex items-center justify-center px-4 text-center text-sm transition-colors hover:text-primary font-semibold text-primary border-b-2 border-b-primary"
          : "flex items-center justify-center px-4 text-center text-sm transition-colors hover:text-primary text-muted-foreground border-b-2 border-b-transparent"
      }
    >
      {children}
    </NavLink>
  );
};

export function EditorNav() {
  return (
    <div className="h-12 border-b border-border/40 bg-background shrink-0">
      <div className="flex h-full gap-4 px-4">
        <Tab to="/editor/summary">전투분석</Tab>
        <Tab to="/editor/log">로그</Tab>
        <Tab to="/editor/chart">차트</Tab>
        <Tab to="/editor/skill-data">스킬데이터</Tab>
        <PreferencePopover>
          <button className="flex gap-1 items-center justify-center px-4 text-center text-sm text-primary pb-0.5">
            <Settings className="w-4 h-4" />
            설정
          </button>
        </PreferencePopover>
      </div>
    </div>
  );
}

export function EditorLayout() {
  const { isLoaded } = usePySimapleBeforeLoad();

  if (!isLoaded) {
    return <Navigate to="/" replace={true} />;
  }

  return (
    <PreferenceProvider>
      <WorkspaceProvider>
        <SkillDataProvider>
          <div className="h-screen flex flex-col">
            <Header />
            <div className="flex h-[calc(100vh-4rem)]">
              <Editor />
              <div className="flex grow flex-col">
                <EditorNav />
                <Outlet />
              </div>
            </div>
          </div>
        </SkillDataProvider>
      </WorkspaceProvider>
    </PreferenceProvider>
  );
}
