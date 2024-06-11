import { SimulationSetting } from "@/sdk/models";
import { Label } from "@radix-ui/react-label";
import * as React from "react";
import { Controller, useForm } from "react-hook-form";
import { useWorkspace } from "../hooks/useWorkspace";
import { Button } from "./ui/button";
import {
  Dialog,
  DialogClose,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "./ui/dialog";
import { Input } from "./ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "./ui/select";

const CreateBaselineSimulatorDialog: React.FC = () => {
  const { createBaselineSimulator } = useWorkspace();
  const { register, getValues, control } = useForm({
    defaultValues: {
      tier: "Legendary",
      jobtype: "archmagefb",
      job_category: "1",
      level: 265,
      use_doping: true,
      passive_skill_level: 0,
      combat_orders_level: 1,
      union_block_count: 37,
      link_count: 12 + 1,
      armor: 300,
      mob_level: 265,
      force_advantage: 1.0,
      trait_level: 100,
      artifact_level: 0,
      v_skill_level: 30,
      v_improvements_level: 60,
      weapon_attack_power: 0,
      weapon_pure_attack_power: 0,
    },
  });
  const [isOpen, setIsOpen] = React.useState(false);
  const [isLoading, setIsLoading] = React.useState(false);

  async function handleSubmit() {
    setIsLoading(true);
    const values = getValues();
    await createBaselineSimulator({
      simulation_setting: {
        tier: values.tier,
        jobtype: values.jobtype as SimulationSetting["jobtype"],
        job_category: Number(values.job_category),
        level: values.level,
        use_doping: values.use_doping,
        passive_skill_level: values.passive_skill_level,
        combat_orders_level: values.combat_orders_level,
        union_block_count: values.union_block_count,
        link_count: values.link_count,
        armor: values.armor,
        mob_level: values.mob_level,
        force_advantage: values.force_advantage,
        trait_level: values.trait_level,
        artifact_level: values.artifact_level,
        v_skill_level: values.v_skill_level,
        v_improvements_level: values.v_improvements_level,
        weapon_attack_power: values.weapon_attack_power,
        weapon_pure_attack_power: values.weapon_pure_attack_power,
      },
    });
    setIsLoading(false);
    setIsOpen(false);
  }

  return (
    <Dialog open={isOpen} onOpenChange={setIsOpen}>
      <DialogTrigger asChild>
        <Button>New</Button>
      </DialogTrigger>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Create Simulator</DialogTitle>
        </DialogHeader>
        <DialogClose />
        <div className="flex flex-col gap-2">
          <Controller
            control={control}
            name="jobtype"
            render={({ field: { name, value, onChange, disabled } }) => (
              <Select
                name={name}
                value={value}
                onValueChange={onChange}
                disabled={disabled}
              >
                <SelectTrigger>
                  <SelectValue placeholder="직업" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="archmagefb">불독</SelectItem>
                  <SelectItem value="archmagetc">썬콜</SelectItem>
                  <SelectItem value="bishop">비숍</SelectItem>
                  <SelectItem value="mechanic">메카닉</SelectItem>
                  <SelectItem value="adele">아델</SelectItem>
                  <SelectItem value="dualblade">듀블</SelectItem>
                  <SelectItem value="soulmaster">소마</SelectItem>
                </SelectContent>
              </Select>
            )}
          />
          <Controller
            control={control}
            name="job_category"
            render={({ field: { name, value, onChange, disabled } }) => (
              <Select
                name={name}
                value={value}
                onValueChange={onChange}
                disabled={disabled}
              >
                <SelectTrigger>
                  <SelectValue placeholder="직업군" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="0">전사</SelectItem>
                  <SelectItem value="1">마법사</SelectItem>
                  <SelectItem value="2">궁수</SelectItem>
                  <SelectItem value="3">도적</SelectItem>
                  <SelectItem value="4">해적</SelectItem>
                </SelectContent>
              </Select>
            )}
          />
          <div className="grid grid-cols-2 gap-x-10 items-center">
            <Label htmlFor="level">레벨</Label>
            <Input id="level" {...register("level")} />
            <Label>몹 레벨</Label>
            <Input {...register("mob_level")} />
            <Label>몹 방어력</Label>
            <Input {...register("armor")} />
            <Label>패시브 스킬 레벨</Label>
            <Input {...register("passive_skill_level")} />
            <Label>컴뱃 오더스 수치</Label>
            <Input {...register("combat_orders_level")} />
            <Label>유니온 배치 칸</Label>
            <Input {...register("union_block_count")} />
            <Label>아티팩트 레벨</Label>
            <Input {...register("artifact_level")} />
            <Label>무기 공격력</Label>
            <Input {...register("weapon_attack_power")} />
            <Label>무기 순수 공격력</Label>
            <Input {...register("weapon_pure_attack_power")} />
          </div>
        </div>

        <DialogFooter>
          <Button disabled={isLoading} onClick={handleSubmit}>
            Create
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
};

export default CreateBaselineSimulatorDialog;
