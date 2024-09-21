import { PlayLogResponse } from "@/sdk/models";

export const MAX_SUPPORTED_CHART_COLOR = 21;

// include 0 and last clock, and 10000 interval
export function getXAxisTicks(logs: PlayLogResponse[]) {
  const lastClock = logs[logs.length - 1].clock;
  const ticks = [0];
  for (let i = 1; i <= lastClock / 10000; i++) {
    ticks.push(i * 10000);
  }
  ticks.push(lastClock);
  return ticks;
}

const colorlist = [
  "#0066CC",
  "#4CB140",
  "#009596",
  "#5752D1",
  "#F4C145",
  "#EC7A08",
  "#7D1007",
  "#8BC1F7",
  "#23511E",
  "#A2D9D9",
  "#2A265F",
  "#F9E0A2",
  "#8F4700",
  "#C9190B",
  "#002F5D",
  "#BDE2B9",
  "#003737",
  "#B2B0EA",
  "#C58C00",
  "#F4B678",
  "#2C0000",
];

export function getColorFromIndex(index: number) {
  return colorlist[index % colorlist.length];
}
