import { PlayLog } from "@/sdk/models";
import {
  default as EChartsReact,
  default as ReactECharts,
} from "echarts-for-react";
import * as React from "react";
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
  const echartsRef = React.useRef<EChartsReact>(null);

  const options = {
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
    <ReactECharts
      ref={echartsRef}
      style={{ height: 200 }}
      option={options}
    ></ReactECharts>
  );
};

const Chart: React.FC<{
  history: PlayLog[];
  setting: ChartSetting;
}> = ({ history, setting }) => {
  const clock = history[history.length - 1].clock;
  const echartsRef = React.useRef<EChartsReact>(null);

  const options = useChart(history, setting);

  React.useEffect(() => {
    echartsRef?.current?.getEchartsInstance().dispatchAction({
      type: "dataZoom",
      endValue: Math.min(clock + 10000, setting.maxClock),
    });
  }, [clock, setting.maxClock]);

  return (
    <div className="w-full h-full p-4">
      <ReactECharts ref={echartsRef} style={{ height: 900 }} option={options} />
      <ShareChart history={history} />
    </div>
  );
};

export default Chart;
