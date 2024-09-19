import { PlayLogResponse } from "@/sdk/models";
import { ChartSetting } from "./preferences.interface.ts";

import * as echarts from "echarts";

const colorlist = [
  "#a6cee3",
  "#1f78b4",
  "#b2df8a",
  "#33a02c",
  "#fb9a99",
  "#e31a1c",
  "#fdbf6f",
  "#ff7f00",
  "#cab2d6",
  "#6a3d9a",
  "#ffff99",
  "#b15928",
];

function getColorFromIndex(index: number) {
  return colorlist[index % colorlist.length];
}

function damageFormatter(value: number) {
  if (value < 10000) return value.toFixed(0);

  if (value < 100000000) return (value / 10000).toFixed(2) + "만";

  if (value < 1000000000000) return (value / 100000000).toFixed(2) + "억";

  return (value / 1000000000000).toFixed(2) + "조";
}

function clockFormatter(value: number) {
  return value + "ms";
}

export function useChart(history: PlayLogResponse[], setting: ChartSetting) {
  const clock = history.length > 0 ? history[history.length - 1].clock : 0;
  const markLine = {
    silent: true,
    animation: true,
    symbol: "none",
    label: {
      show: false,
    },
    lineStyle: {
      type: "solid",
      color: "#bcbcbc",
    },
    data: [
      {
        xAxis: clock,
      },
    ],
  };

  const grid = setting.stackView.show
    ? [{ bottom: "70%" }, { top: "35%", bottom: "35%" }, { top: "70%" }]
    : [{ bottom: "70%" }, { top: "35%" }];
  const xAxis = [
    {
      type: "value",
      gridIndex: 0,
      min: 0,
      max: setting.maxClock,
      axisLabel: {
        formatter: clockFormatter,
      },
    },
    {
      type: "value",
      gridIndex: 1,
      min: 0,
      max: setting.maxClock,
      axisLabel: {
        formatter: clockFormatter,
      },
    },
    ...(setting.stackView.show
      ? [
          {
            type: "value",
            gridIndex: 2,
            min: 0,
            max: setting.maxClock,
            axisLabel: {
              formatter: clockFormatter,
            },
          },
        ]
      : []),
  ];
  const yAxis = [
    {
      type: "value",
      gridIndex: 0,
      axisLabel: {
        formatter: damageFormatter,
      },
    },
    {
      type: "value",
      gridIndex: 0,
      axisLabel: {
        formatter: damageFormatter,
      },
    },
    {
      type: "category",
      gridIndex: 1,
      data: setting.runningView.skillNames,
    },
    ...(setting.stackView.show
      ? [
          {
            type: "value",
            gridIndex: 2,
            min: 0,
            max: setting.stackView.axis1.max,
          },
          {
            type: "value",
            gridIndex: 2,
            min: 0,
            max: setting.stackView.axis2.max,
          },
        ]
      : []),
  ];

  function getCumsumSeries(history: PlayLogResponse[]) {
    const data = history.map((log, index) => {
      return {
        name: log.action.name,
        value: [
          log.clock,
          history.slice(0, index + 1).reduce((sum, log) => sum + log.damage, 0),
        ],
      };
    });

    return {
      name: "누적 데미지",
      data,
      type: "line",
      smooth: true,
      showSymbol: false,
      markLine: markLine,
    };
  }

  function getHistogramSeries(history: PlayLogResponse[]) {
    const chunks: PlayLogResponse[][] = [];

    const timeSlice = 5000;
    for (const playLog of history) {
      while (playLog.clock >= timeSlice * chunks.length) {
        chunks.push([]);
      }
      chunks[chunks.length - 1].push(playLog);
    }

    const data = chunks.map((chunk, index) => {
      return {
        name: `${index * timeSlice}-${(index + 1) * timeSlice}`,
        value: [
          (index + 0.5) * timeSlice,
          chunk.reduce((sum, x) => sum + x.damage, 0),
        ],
      };
    });

    return {
      name: "구간 데미지",
      data,
      type: "bar",
      barMinWidth: 2,
      barMaxWidth: 50,
      clip: true,
      yAxisIndex: 1,
    };
  }

  function getUptimeSeries(history: PlayLogResponse[]) {
    const names = setting.runningView.skillNames;
    const data = names.flatMap((name, i) => {
      return history
        .filter(
          (log) =>
            log.events.find(
              (event) => event.name === name && event.method === "use",
            ) && log.running_view[name].time_left > 0,
        )
        .map((log) => ({
          name,
          value: [
            i,
            log.clock,
            Math.min(
              log.clock + log.running_view[name].time_left,
              setting.maxClock,
            ),
          ],
          itemStyle: {
            normal: {
              color: getColorFromIndex(i),
            },
          },
        }));
    });

    return {
      data,
      renderItem: renderUptime,
      encode: {
        x: [1, 2],
        y: 0,
      },
      type: "custom",
      xAxisIndex: 1,
      yAxisIndex: 2,
      markLine: markLine,
    };
  }

  function getStackSeries(history: PlayLogResponse[], { stackView }: ChartSetting) {
    if (!stackView.show) return [];

    const getSeries = (names: string[], yAxisIndex: number) =>
      names.map((name) => {
        const stacks = history
          .filter((log, index) => log.clock !== history[index + 1]?.clock)
          .map((log) => [log.clock, log.running_view[name].stack]);
        return {
          name,
          type: "line",
          data: stacks,
          xAxisIndex: 2,
          yAxisIndex,
          smooth: false,
          showSymbol: false,
          markLine: markLine,
        };
      });

    return [
      ...getSeries(stackView.axis1.skillNames, 3),
      ...getSeries(stackView.axis2.skillNames, 4),
    ];
  }

  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  function renderUptime(params: any, api: any) {
    const categoryIndex = api.value(0);
    const start = api.coord([api.value(1), categoryIndex]);
    const end = api.coord([api.value(2), categoryIndex]);
    const height = api.size([0, 1])[1] * 0.6;

    const rectShape = echarts.graphic.clipRectByRect(
      {
        x: start[0],
        y: start[1] - height / 2,
        width: end[0] - start[0],
        height: height,
      },
      {
        x: params.coordSys.x,
        y: params.coordSys.y,
        width: params.coordSys.width,
        height: params.coordSys.height,
      },
    );
    return (
      rectShape && {
        type: "rect",
        transition: ["shape"],
        shape: rectShape,
        style: api.style(),
      }
    );
  }

  return {
    grid,
    axisPointer: {
      link: [
        {
          xAxisIndex: "all",
        },
      ],
    },
    tooltip: {
      trigger: "axis",
      axisPointer: {
        type: "cross",
        animation: false,
      },
    },
    toolbox: {
      feature: {
        dataZoom: {
          yAxisIndex: "none",
        },
        saveAsImage: {},
      },
    },
    dataZoom: [
      {
        show: true,
        realtime: true,
        xAxisIndex: setting.stackView.show ? [0, 1, 2] : [0, 1],
        filterMode: "weakFilter",
      },
      {
        type: "inside",
        realtime: true,
        xAxisIndex: setting.stackView.show ? [0, 1, 2] : [0, 1],
        filterMode: "weakFilter",
      },
    ],
    xAxis,
    yAxis,
    series: [
      getCumsumSeries(history),
      getHistogramSeries(history),
      getUptimeSeries(history),
      ...getStackSeries(history, setting),
    ],
  };
}
