import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Checkbox } from "@/components/ui/checkbox";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { usePreference } from "@/hooks/usePreference";
import { Controller, useForm } from "react-hook-form";

export function PreferencePage() {
  const { preferences, setPreferences } = usePreference();
  const { register, control, getValues, watch } = useForm({
    defaultValues: {
      startClock: preferences.startClock / 1000,
      useDuration: preferences.duration !== null,
      duration:
        preferences.duration === null ? null : preferences.duration / 1000,
    },
  });

  function handleSave() {
    const { startClock, useDuration, duration } = getValues();
    setPreferences({
      startClock: Number(startClock) * 1000,
      duration: useDuration ? Number(duration) * 1000 : null,
    });
  }

  return (
    <div className="flex flex-col grow gap-2 p-4">
      <Card>
        <CardHeader>
          <CardTitle>측정시간 설정</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex flex-col gap-3">
            <div className="flex gap-2 items-center">
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
            <div className="flex gap-2 items-center">
              <Label htmlFor="startClock">시작 시각 (초)</Label>
              <Input
                id="startClock"
                className="w-32"
                type="number"
                {...register("startClock")}
              />
            </div>

            {watch("useDuration") && (
              <div className="flex gap-2 items-center">
                <Label htmlFor="duration">측정 시간 (초)</Label>
                <Input
                  id="duration"
                  className="w-32"
                  type="number"
                  {...register("duration")}
                />
              </div>
            )}
          </div>
        </CardContent>
        <CardFooter>
          <Button onClick={() => handleSave()}>저장</Button>
        </CardFooter>
      </Card>
    </div>
  );
}
