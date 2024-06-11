import * as React from "react";
import CreateBaselineSimulatorDialog from "./CreateBaselineSimulatorDialog";
import ChartSettingDialog from "./ChartSettingDialog";

const Header: React.FC = () => {
  return (
    <header className="px-8 border-bw-full border-b border-border/40 bg-background">
      <div className="flex h-14 items-center gap-2">
        <div className="font-semibold">Simaple</div>
        <CreateBaselineSimulatorDialog />
        <ChartSettingDialog />
      </div>
    </header>
  );
};

export default Header;
