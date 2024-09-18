export interface ChartSetting {
  maxClock: number;
  runningView: {
    skillNames: string[];
  };
  stackView: {
    show: boolean;
    axis1: {
      max: number;
      skillNames: string[];
    };
    axis2: {
      max: number;
      skillNames: string[];
    };
  };
}

export interface Preferences {
  chart: ChartSetting;
}
