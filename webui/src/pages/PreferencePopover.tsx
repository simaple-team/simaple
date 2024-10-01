import { Button } from "@/components/ui/button";
import { Checkbox } from "@/components/ui/checkbox";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover";
import { usePreference } from "@/hooks/usePreference";
import { Controller, useForm } from "react-hook-form";

interface PreferencePopoverProps {
  children?: React.ReactNode;
}

interface PreferenceForm {
  startClock: number;
  useDuration: boolean;
  duration: number | null;
}

export function PreferencePopover(props: PreferencePopoverProps) {
  const { preferences, setPreferences } = usePreference();
  const { register, control, watch, handleSubmit } = useForm<PreferenceForm>({
    defaultValues: {
      startClock: preferences.startClock / 1000,
      useDuration: preferences.duration !== null,
      duration:
        preferences.duration === null ? null : preferences.duration / 1000,
    },
  });

  function handleSave(data: PreferenceForm) {
    const { startClock, useDuration, duration } = data;
    setPreferences({
      startClock: Number(startClock) * 1000,
      duration: useDuration ? Number(duration) * 1000 : null,
    });
  }

  return (
    <Popover>
      <PopoverTrigger asChild>{props.children}</PopoverTrigger>
      <PopoverContent className="w-96">
        <form className="grid gap-4" onSubmit={handleSubmit(handleSave)}>
          <div className="space-y-2">
            <h4 className="font-medium leading-none">시간 설정</h4>
            <p className="text-sm text-muted-foreground">
              시뮬레이션 시작 시각과 측정 시간을 설정합니다.
            </p>
          </div>
          <div className="flex items-center gap-2">
            <Controller
              name="useDuration"
              control={control}
              render={({ field: { value, onChange } }) => (
                <Checkbox
                  id="useDuration"
                  checked={value}
                  onCheckedChange={onChange}
                />
              )}
            />
            <Label htmlFor="useDuration">측정 시간 사용</Label>
          </div>
          <div className="grid gap-2">
            <div className="grid grid-cols-2 items-center gap-4">
              <Label htmlFor="startClock">시작 시각 (초)</Label>
              <Input
                id="startClock"
                className="h-8"
                type="number"
                step=".01"
                {...register("startClock")}
              />
            </div>
            {watch("useDuration") && (
              <div className="grid grid-cols-2 items-center gap-4">
                <Label htmlFor="duration">측정 시간 (초)</Label>
                <Input
                  id="duration"
                  className="h-8"
                  type="number"
                  step=".01"
                  {...register("duration")}
                />
              </div>
            )}
          </div>
          <Button type="submit">저장</Button>
        </form>
      </PopoverContent>
    </Popover>
  );
}
