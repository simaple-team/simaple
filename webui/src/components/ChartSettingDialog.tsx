import * as React from "react";
import { Controller, useForm } from "react-hook-form";
import { ChartSetting } from "../hooks/preferences.interface";
import { usePreference } from "../hooks/usePreference";
import { useWorkspace } from "../hooks/useWorkspace";
import { Button } from "./ui/button";
import { Checkbox } from "./ui/checkbox";
import {
  Dialog,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "./ui/dialog";
import { Input } from "./ui/input";
import { Label } from "./ui/label";

const ChartSettingDialog: React.FC = () => {
  const { chartSetting, setChartSetting } = usePreference();
  const { history } = useWorkspace();
  const { register, control, getValues } = useForm<ChartSetting>({
    defaultValues: chartSetting,
  });
  const [isOpen, setIsOpen] = React.useState(false);

  const runningView = history[0]?.running_view;

  const skillNames = React.useMemo(
    () =>
      runningView
        ? Object.keys(runningView).filter(
            (name) => runningView[name].stack != null,
          )
        : [],
    [runningView],
  );

  async function handleSubmit() {
    setChartSetting(getValues());
    setIsOpen(false);
  }

  return (
    <Dialog open={isOpen} onOpenChange={setIsOpen}>
      <DialogTrigger asChild>
        <Button>차트 설정</Button>
      </DialogTrigger>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>차트 설정</DialogTitle>
        </DialogHeader>
        <div className="flex flex-col gap-2">
          <div className="flex gap-2">
            <Label htmlFor="showStackChart">스택 차트 표시</Label>
            <Controller
              name="showStackChart"
              control={control}
              render={({ field: { value, onChange } }) => (
                <Checkbox
                  id="showStackChart"
                  checked={value}
                  onCheckedChange={onChange}
                />
              )}
            />
          </div>
          <div className="flex flex-col gap-2">
            <span className="text-sm">스택 그룹 1</span>
            <Label htmlFor="stackAxis1.max">Max</Label>
            <Input id="stackAxis1.max" {...register("stackAxis1.max")} />
            <Controller
              name={`stackAxis1.skillNames`}
              control={control}
              render={({ field: { value, onChange } }) => (
                <div className="flex gap-1">
                  {skillNames.map((skillName, i) => (
                    <div className="flex gap-1 items-center">
                      <Checkbox
                        id={`stackAxis1.skillNames.${i}`}
                        key={skillName}
                        checked={value.includes(skillName)}
                        onCheckedChange={
                          value.includes(skillName)
                            ? () =>
                                onChange(
                                  value.filter((name) => name !== skillName),
                                )
                            : () => onChange([...value, skillName])
                        }
                      />
                      <Label htmlFor={`stackAxis1.skillNames.${i}`}>
                        {skillName}
                      </Label>
                    </div>
                  ))}
                </div>
              )}
            />
          </div>
          <div className="flex flex-col gap-2">
            <span className="text-sm">스택 그룹 2</span>
            <Label htmlFor="stackAxis2.max">Max</Label>
            <Input id="stackAxis2.max" {...register("stackAxis2.max")} />
            <Controller
              name="stackAxis2.skillNames"
              control={control}
              render={({ field: { value, onChange } }) => (
                <div className="flex gap-1">
                  {skillNames.map((skillName, i) => (
                    <div className="flex gap-1 items-center">
                      <Checkbox
                        id={`stackAxis2.skillNames.${i}`}
                        key={skillName}
                        checked={value.includes(skillName)}
                        onCheckedChange={
                          value.includes(skillName)
                            ? () =>
                                onChange(
                                  value.filter((name) => name !== skillName),
                                )
                            : () => onChange([...value, skillName])
                        }
                      />
                      <Label htmlFor={`stackAxis2.skillNames.${i}`}>
                        {skillName}
                      </Label>
                    </div>
                  ))}
                </div>
              )}
            />
          </div>
        </div>

        <DialogFooter>
          <Button onClick={handleSubmit}>저장</Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
};

export default ChartSettingDialog;
