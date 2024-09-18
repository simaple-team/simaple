import * as React from "react";
import { ChartSetting, Preferences } from "./preferences.interface";

type PreferenceProviderProps = { children: React.ReactNode };

function usePreferenceState() {
  const [preferences, setPreferences] = React.useState<Preferences>({
    chart: {
      maxClock: 180 * 1000,
      runningView: {
        skillNames: [],
      },
      stackView: {
        show: false,
        axis1: {
          max: 10,
          skillNames: [],
        },
        axis2: {
          max: 10,
          skillNames: [],
        },
      },
    },
  });

  function setChartSetting(chart: ChartSetting) {
    setPreferences({
      ...preferences,
      chart,
    });
  }

  const { chart: chartSetting } = preferences;

  return {
    chartSetting,
    setChartSetting,
  };
}

const PreferenceStateContext = React.createContext<
  ReturnType<typeof usePreferenceState> | undefined
>(undefined);

function PreferenceProvider({ children }: PreferenceProviderProps) {
  const value = usePreferenceState();

  return (
    <PreferenceStateContext.Provider value={value}>
      {children}
    </PreferenceStateContext.Provider>
  );
}

function usePreference() {
  const context = React.useContext(PreferenceStateContext);
  if (context === undefined) {
    throw new Error("usePreference must be used within a PreferenceProvider");
  }
  return context;
}

export { PreferenceProvider, usePreference };
