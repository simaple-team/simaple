"use client";

import { CartesianGrid, Line, LineChart, XAxis } from "recharts";

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
  ChartTooltip,
  ChartTooltipContent,
} from "@/components/ui/chart";
import { useWorkspace } from "@/hooks/useWorkspace";
import { secFormatter } from "@/lib/formatters";
import { getStack } from "@/lib/statistics";
import { useMemo, useState } from "react";
import { Label } from "../../components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "../../components/ui/select";

const chartConfig = {
  stack: {
    label: "스택",
    color: "var(--chart-6)",
  },
} satisfies ChartConfig;

export function StackChart() {
  const { history: logs } = useWorkspace();
  const runningView = logs[0]?.running_view;
  const skillNames = useMemo(
    () => (runningView ? Object.keys(runningView) : []),
    [runningView],
  );
  const stackSkillNames = useMemo(
    () => skillNames.filter((name) => runningView[name].stack != null),
    [runningView, skillNames],
  );
  const [selectedSkillName, setSelectedSkillName] = useState<string>(
    stackSkillNames[0] ?? "",
  );
  const data = useMemo(
    () => (selectedSkillName ? getStack(logs, selectedSkillName) : []),
    [logs, selectedSkillName],
  );

  if (stackSkillNames.length === 0) {
    return null;
  }

  return (
    <Card className="max-w-[1200px]">
      <CardHeader>
        <CardTitle>스택</CardTitle>
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
              tickLine={false}
              axisLine={false}
              tickMargin={8}
              tickFormatter={(value) => secFormatter(value)}
            />
            <ChartTooltip
              cursor={false}
              content={<ChartTooltipContent hideLabel />}
            />
            <Line
              dataKey="stack"
              type="step"
              stroke="var(--color-stack)"
              strokeWidth={2}
              dot={false}
            />
          </LineChart>
        </ChartContainer>
      </CardContent>
      <CardFooter className="flex-col items-start gap-2 text-sm">
        <div className="flex items-center gap-2">
          <Label>스킬</Label>
          <Select
            value={selectedSkillName}
            onValueChange={setSelectedSkillName}
          >
            <SelectTrigger className="w-80">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              {stackSkillNames.map((name) => (
                <SelectItem key={name} value={name}>
                  {name}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
      </CardFooter>
    </Card>
  );
}
