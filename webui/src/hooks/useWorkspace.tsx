import { useContext } from "react";
import { WorkspaceStateContext } from "./useWorkspaceState";

function useWorkspace() {
  const context = useContext(WorkspaceStateContext);
  if (context === undefined) {
    throw new Error("useWorkspace must be used within a WorkspaceProvider");
  }
  return context;
}

export { useWorkspace };
