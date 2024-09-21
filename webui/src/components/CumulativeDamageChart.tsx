import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  ChartConfig,
  ChartContainer,
  ChartTooltip,
  ChartTooltipContent,
} from "@/components/ui/chart";
import { getXAxisTicks } from "@/lib/chart";
import { damageFormatter, secFormatter } from "@/lib/formatters";
import { getCumulativeDamage } from "@/lib/statistics";
import { PlayLogResponse } from "@/sdk/models";
import { useMemo } from "react";
import { CartesianGrid, Line, LineChart, XAxis, YAxis } from "recharts";

const chartConfig = {
  damage: {
    label: "데미지",
    color: "var(--chart-6)",
  },
} satisfies ChartConfig;

interface CumulativeDamageChartProps {
  logs: PlayLogResponse[];
}

export function CumulativeDamageChart({ logs }: CumulativeDamageChartProps) {
  const data = useMemo(() => getCumulativeDamage(logs), [logs]);
  const ticks = useMemo(() => getXAxisTicks(logs), [logs]);

  return (
    <Card>
      <CardHeader>
        <CardTitle>누적 데미지</CardTitle>
      </CardHeader>
      <CardContent>
        <ChartContainer config={chartConfig}>
          <LineChart
            accessibilityLayer
            data={data}
            margin={{
              left: 12,
              right: 12,
            }}
          >
            <CartesianGrid vertical={false} />
            <XAxis
              type="number"
              dataKey="clock"
              scale="time"
              interval={0}
              axisLine={false}
              ticks={ticks}
              tickFormatter={(value) => secFormatter(value)}
            />
            <YAxis
              tickLine={false}
              tickMargin={10}
              axisLine={false}
              tickFormatter={(value) => damageFormatter(value)}
            />
            <ChartTooltip
              cursor={false}
              content={
                <ChartTooltipContent
                  formatter={(value, name) => (
                    <div className="flex min-w-[130px] items-center text-xs text-muted-foreground">
                      {chartConfig[name as keyof typeof chartConfig]?.label ||
                        name}
                      <div className="ml-auto flex items-baseline gap-0.5 font-mono font-medium tabular-nums text-foreground">
                        {damageFormatter(value as number)}
                      </div>
                    </div>
                  )}
                  hideLabel
                />
              }
            />
            <Line
              dataKey="damage"
              type="linear"
              stroke="var(--color-damage)"
              strokeWidth={2}
              dot={false}
            />
          </LineChart>
        </ChartContainer>
      </CardContent>
    </Card>
  );
}
