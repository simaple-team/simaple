import { Button } from "@/components/ui/button";
import { usePySimaple } from "@/hooks/useSimaple";
import { Loader2 } from "lucide-react";
import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

const LOADING_MESSAGES = [
  "펭귄에게 먹이를 주는 중...",
  "데이터를 불러오는 중...",
  "하인즈의 턱수염을 빗는 중...",
  "유니온 테트리스를 하는 중...",
  "로딩 중...",
];

function LoadingText() {
  const [message, setMessage] = useState(
    LOADING_MESSAGES[Math.floor(Math.random() * LOADING_MESSAGES.length)],
  );

  useEffect(() => {
    const interval = setInterval(() => {
      setMessage(
        LOADING_MESSAGES[Math.floor(Math.random() * LOADING_MESSAGES.length)],
      );
    }, 2000);

    return () => clearInterval(interval);
  }, []);

  return <span>{message}</span>;
}

export function PrepareSimaple() {
  const navigate = useNavigate();
  const { load, isLoading, isLoaded } = usePySimaple();

  useEffect(() => {
    if (isLoaded) {
      navigate("/editor/summary");
    }
  }, [isLoaded, navigate]);

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
