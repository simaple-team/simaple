import { Label } from "@radix-ui/react-label";
import { Loader2 } from "lucide-react";
import * as React from "react";
import { useState } from "react";
import { useForm } from "react-hook-form";
import { useWorkspace } from "../hooks/useWorkspace";
import { Button } from "./ui/button";
import {
  DialogClose,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "./ui/dialog";
import { Input } from "./ui/input";

function getYesterday(): string {
  const yesterday = new Date();
  yesterday.setDate(yesterday.getDate() - 1);
  return yesterday.toISOString().split("T")[0];
}

const CreateNexonApiFileDialog: React.FC<{
  onSubmit: () => void;
}> = ({ onSubmit }) => {
  const { setPlan, getInitialPlanFromMetadata } = useWorkspace();
  const { register, getValues } = useForm({
    defaultValues: {
      character_name: "",
      date: getYesterday(),
      token: "",
    },
  });
  const [isLoading, setIsLoading] = useState(false);

  async function handleSubmit() {
    const values = getValues();
    setIsLoading(true);
    await getInitialPlanFromMetadata({
      author: values.character_name,
      provider: {
        name: "NexonAPIEnvironmentProvider",
        data: {
          character_name: values.character_name,
          date: values.date,
          token: values.token,
        },
      },
    }).match(
      (plan) => {
        setPlan(plan);
      },
      (err) => console.error(err),
    );
    onSubmit();
    setIsLoading(false);
  }

  return (
    <DialogContent>
      <DialogHeader>
        <DialogTitle>새 파일</DialogTitle>
      </DialogHeader>
      <DialogClose />
      <div className="flex flex-col gap-2">
        <div className="grid grid-cols-2 gap-x-10 items-center">
          <Label htmlFor="level">캐릭터명</Label>
          <Input id="character_name" {...register("character_name")} />
          <Label>날짜</Label>
          <Input {...register("date")} />
          <Label>API 토큰</Label>
          <Input {...register("token")} />
        </div>
      </div>

      <DialogFooter>
        <Button disabled={isLoading} onClick={handleSubmit}>
          {isLoading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
          Create
        </Button>
      </DialogFooter>
    </DialogContent>
  );
};

export default CreateNexonApiFileDialog;
