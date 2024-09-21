import * as React from "react";
import { Preferences } from "./preferences.interface";

type PreferenceProviderProps = { children: React.ReactNode };

function usePreferenceState() {
  const [preferences, setPreferences] = React.useState<Preferences>({
    startClock: 0,
    duration: null,
  });

  return {
    preferences,
    setPreferences,
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
