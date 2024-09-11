import { Button } from "@/components/ui/button";
import { usePySimapleBeforeLoad } from "@/hooks/useSimaple";
import { Loader2 } from "lucide-react";
import { useEffect } from "react";
import { useState } from "react";

function LoadingText() {
  const messages = [
    "펭귄에게 먹이를 주는 중...",
    "데이터를 불러오는 중...",
    "하인즈의 턱수염을 빗는 중...",
    "유니온 테트리스를 하는 중...",
    "로딩 중...",
  ];

  const [message, setMessage] = useState(
    messages[Math.floor(Math.random() * messages.length)],
  );

  useEffect(() => {
    const interval = setInterval(() => {
      setMessage(messages[Math.floor(Math.random() * messages.length)]);
    }, 2000);

    return () => clearInterval(interval);
  }, []);

  return <span>{message}</span>;
}

export function PrepareSimaple() {
  const { load, isLoading } = usePySimapleBeforeLoad();

  return (
    <div className="h-screen flex flex-col justify-center items-center">
      <div className="rounded-lg border bg-card text-card-foreground shadow-sm">
        <div className="flex flex-col p-6">
          <h1 className="text-xl font-bold">환영합니다!</h1>
          <p>Simaple은 메이플스토리 전투 환경을 시뮬레이션하는 도구입니다.</p>
        </div>
        <div className="flex flex-col p-6 pt-0">
          <Button disabled={isLoading} onClick={load}>
            {isLoading ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                <LoadingText />
              </>
            ) : (
              "시작하기"
            )}
          </Button>
        </div>
      </div>
    </div>
  );
}
