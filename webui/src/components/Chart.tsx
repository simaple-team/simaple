import { PlayLog } from "@/sdk/models";
import { useThrottledState } from "@react-hookz/web";
import { EChartsOption, default as ReactECharts } from "echarts-for-react";
import React, { useEffect, useMemo, useRef } from "react";
import { ChartSetting } from "../hooks/preferences.interface";
import { useChart } from "../hooks/useChart";

function getTotalData(history: PlayLog[]) {
  const record = history
    .flatMap((history) => history.damages)
    .reduce(
      (obj, [name, damage]) => {
        if (!obj[name]) {
          obj[name] = 0;
        }
        obj[name] += damage;
        return obj;
      },
      {} as Record<string, number>,
    );

  return Object.entries(record)
    .map(([name, value]) => ({
      name,
      value,
    }))
    .sort((a, b) => b.value - a.value);
}

const ShareChart: React.FC<{ history: PlayLog[] }> = ({ history }) => {
  const echartsRef = useRef<ReactECharts>(null);

  const options: EChartsOption = {
    tooltip: {
      trigger: "item",
      formatter: "{a} <br/>{b} : {c} ({d}%)",
    },
    series: [
      {
        name: "Share",
        type: "pie",
        radius: [20, 100],
        center: ["50%", "50%"],
        roseType: "radius",
        label: {
          formatter: "{b} ({d}%)",
        },
        itemStyle: {
          borderRadius: 5,
        },
        emphasis: {
          label: {
            show: true,
          },
        },
        data: getTotalData(history),
      },
    ],
  };

  return (
    <ReactECharts ref={echartsRef} style={{ height: 200 }} option={options} />
  );
};

const Chart: React.FC<{
  history: PlayLog[];
  setting: ChartSetting;
}> = ({ history, setting }) => {
  const clock = history.length > 0 ? history[history.length - 1].clock : 0;
  const echartsRef = useRef<ReactECharts>(null);

  const [range, setRange] = useThrottledState<[number, number]>(
    [0, clock + 10000],
    200,
  );

  const options = useChart(history, setting);
  const historyInRange = useMemo(
    () =>
      history.filter((log) => log.clock >= range[0] && log.clock <= range[1]),
    [history, range],
  );

  useEffect(() => {
    echartsRef?.current?.getEchartsInstance().dispatchAction({
      type: "dataZoom",
      endValue: Math.min(clock + 10000, setting.maxClock),
    });
  }, [clock, setting.maxClock]);

  return (
    <div className="w-full h-full p-4">
      <ReactECharts
        ref={echartsRef}
        style={{ height: 900 }}
        option={options}
        onEvents={useMemo(
          () => ({
            datazoom: (
              _: unknown,
              chart: {
                getOption: () => {
                  dataZoom: { startValue: number; endValue: number }[];
                };
              },
            ) => {
              const option = chart.getOption();

              if (!option) return;

              setRange([
                option.dataZoom[0].startValue,
                option.dataZoom[0].endValue + 1,
              ]);
            },
          }),
          [],
        )}
      />
      <ShareChart history={historyInRange} />
    </div>
  );
};

export default Chart;
