import * as React from "react";
import CreateBaselineSimulatorDialog from "./CreateBaselineSimulatorDialog";
import ChartSettingDialog from "./ChartSettingDialog";
import { Button } from "./ui/button";
import { Link } from "react-router-dom";

const Header: React.FC = () => {
  return (
    <header className="px-8 border-bw-full border-b border-border/40 bg-background">
      <div className="flex h-14 items-center gap-2">
        <div className="font-semibold">Simaple</div>
        <CreateBaselineSimulatorDialog />
        <ChartSettingDialog />
        <Button asChild>
          <Link to="/editor/chart">차트뷰</Link>
        </Button>
        <Button asChild>
          <Link to="/editor/log">로그뷰</Link>
        </Button>
      </div>
    </header>
  );
};

export default Header;
