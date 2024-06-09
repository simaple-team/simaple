import * as React from "react";
import { ChartSetting, Preferences } from "./preferences.interface";

type PreferenceProviderProps = { children: React.ReactNode };

function usePreferenceState() {
  const [preferences, setPreferences] = React.useState<Preferences>({
    chart: {
      maxClock: 180 * 1000,
      stackAxis1: {
        max: 10,
        skillNames: [],
      },
      stackAxis2: {
        max: 10,
        skillNames: [],
      },
    },
    autoElapse: true,
  });

  function setChartSetting(chart: ChartSetting) {
    setPreferences({
      ...preferences,
      chart,
    });
  }

  function setAutoElapse(autoElapse: boolean) {
    setPreferences({
      ...preferences,
      autoElapse,
    });
  }

  const { chart: chartSetting, autoElapse } = preferences;

  return {
    chartSetting,
    autoElapse,
    setChartSetting,
    setAutoElapse,
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
