"use client";

import { Bar, BarChart, CartesianGrid, XAxis, YAxis } from "recharts";

import {
  Card,
  CardContent,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  ChartConfig,
  ChartContainer,
  ChartLegend,
  ChartLegendContent,
  ChartTooltip,
  ChartTooltipContent,
} from "@/components/ui/chart";
import { PlayLogResponse } from "@/sdk/models";
import { getIntervalDamage, getSkillNamesDamageDesc } from "@/lib/statistics";
import { useMemo, useState } from "react";
import { damageFormatter, secFormatter } from "@/lib/formatters";
import { MAX_SUPPORTED_CHART_COLOR } from "@/lib/chart";
import { Label } from "./ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "./ui/select";

interface IntervalDamageChartProps {
  logs: PlayLogResponse[];
}

function grayscale(total: number, index: number): string {
  const grayscaleValue = Math.floor((index / total) * 255);
  const hexValue = grayscaleValue.toString(16).padStart(2, "0");
  return `#${hexValue}${hexValue}${hexValue}`;
}

export function IntervalDamageChart({ logs }: IntervalDamageChartProps) {
  const [interval, setInterval] = useState(10000);
  const skillNames = useMemo(() => getSkillNamesDamageDesc(logs), [logs]);
  const data = useMemo(
    () => getIntervalDamage(logs, interval),
    [logs, skillNames, interval],
  );

  const chartConfig = Object.fromEntries(
    skillNames.map((skillName, index) => {
      return [
        skillName,
        {
          label: skillName,
          color:
            index < MAX_SUPPORTED_CHART_COLOR
              ? `var(--chart-${index + 1})`
              : grayscale(
                  skillNames.length - MAX_SUPPORTED_CHART_COLOR,
                  index - MAX_SUPPORTED_CHART_COLOR,
                ),
        },
      ];
    }),
  ) satisfies ChartConfig;

  return (
    <Card>
      <CardHeader>
        <CardTitle>구간 데미지</CardTitle>
      </CardHeader>
      <CardContent>
        <ChartContainer config={chartConfig}>
          <BarChart accessibilityLayer data={data}>
            <CartesianGrid vertical={false} />
            <XAxis
              dataKey="end"
              tickLine={false}
              tickMargin={10}
              axisLine={false}
              tickFormatter={(value) => secFormatter(value)}
            />
            <YAxis
              tickLine={false}
              tickMargin={10}
              axisLine={false}
              tickFormatter={(value) => damageFormatter(value)}
            />
            <ChartTooltip
              content={
                <ChartTooltipContent
                  hideLabel
                  className="w-[240px]"
                  formatter={(value, name) => (
                    <>
                      <div
                        className="h-2.5 w-2.5 shrink-0 rounded-[2px] bg-[--color-bg]"
                        style={
                          {
                            "--color-bg": chartConfig[name].color,
                          } as React.CSSProperties
                        }
                      />
                      {chartConfig[name as keyof typeof chartConfig]?.label ||
                        name}
                      <div className="ml-auto flex items-baseline gap-0.5 font-mono font-medium tabular-nums text-foreground">
                        {damageFormatter(value as number)}
                      </div>
                    </>
                  )}
                />
              }
            />
            <ChartLegend
              content={<ChartLegendContent />}
              className="grid grid-template-auto gap-2"
            />
            {skillNames.map((skillName) => (
              <Bar
                key={skillName}
                dataKey={skillName}
                stackId="a"
                fill={chartConfig[skillName].color}
              />
            ))}
          </BarChart>
        </ChartContainer>
      </CardContent>
      <CardFooter className="flex-col items-start gap-2 text-sm">
        <div className="flex items-center gap-2">
          <Label>구간</Label>
          <Select
            value={interval.toString()}
            onValueChange={(x) => setInterval(Number(x))}
          >
            <SelectTrigger className="w-80">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="5000">5초</SelectItem>
              <SelectItem value="10000">10초</SelectItem>
            </SelectContent>
          </Select>
        </div>
      </CardFooter>
    </Card>
  );
}
