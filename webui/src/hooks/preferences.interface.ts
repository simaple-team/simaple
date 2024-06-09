export interface ChartSetting {
  maxClock: number;
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
  autoElapse: boolean;
}
