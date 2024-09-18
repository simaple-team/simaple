export interface ChartSetting {
  maxClock: number;
  showStackChart: boolean;
  stackAxis1: {
    max: number;
    skillNames: string[];
  };
  stackAxis2: {
    max: number;
    skillNames: string[];
  };
}

export interface Preferences {
  chart: ChartSetting;
}
