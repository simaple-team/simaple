import { Button } from "@/components/ui/button";
import {
  autocompletion,
  CompletionContext,
  CompletionResult,
} from "@codemirror/autocomplete";
import CodeMirror, { EditorView } from "@uiw/react-codemirror";
import * as React from "react";
import Chart from "../components/Chart";
import { usePreference } from "../hooks/usePreference";
import { useWorkspace } from "../hooks/useWorkspace";

function ensureAnchor(expr: RegExp, start: boolean) {
  const { source } = expr;
  const addStart = start && source[0] != "^";
  const addEnd = source[source.length - 1] != "$";
  if (!addStart && !addEnd) return expr;
  return new RegExp(
    `${addStart ? "^" : ""}(?:${source})${addEnd ? "$" : ""}`,
    expr.flags ?? (expr.ignoreCase ? "i" : ""),
  );
}

function matchBefore(context: CompletionContext, expr: RegExp) {
  const line = context.state.doc.lineAt(context.pos);
  const start = Math.max(line.from, context.pos - 250);
  const str = line.text.slice(start - line.from, context.pos - line.from + 1);
  const found = str.search(ensureAnchor(expr, false));

  return found < 0
    ? null
    : { from: start + found, to: context.pos, text: str.slice(found) };
}

function createCompletion(skillNames: string[]) {
  const completions = skillNames.map((name) => ({
    label: name,
    type: "constant",
  }));

  function myCompletions(context: CompletionContext): CompletionResult | null {
    const before = matchBefore(context, /([가-힣]+|\w+)/);

    // If completion wasn't explicitly started and there
    // is no word before the cursor, don't open completions.
    if (!context.explicit && !before) return null;
    return {
      from: before ? before.from : context.pos,
      to: before ? before.to : undefined,
      options: completions,
      validFor: /^([가-힣]*|\w*)$/,
    };
  }

  return myCompletions;
}

const myTheme = EditorView.theme({
  "&": { height: "100%" },
  ".cm-scroller": { overflow: "auto" },
});

const Editor: React.FC = () => {
  const { history, playLog, skillNames, run } = useWorkspace();
  const { chartSetting } = usePreference();
  const [plan, setPlan] = React.useState("");

  const myCompletions = React.useMemo(
    () => createCompletion(skillNames),
    [skillNames],
  );

  if (!playLog) {
    return <></>;
  }

  function handleRun() {
    run(plan);
  }

  return (
    <div className="flex h-[calc(100vh-4rem)]">
      <div className="flex h-full flex-col shrink-0 w-[520px] p-4 gap-2 border">
        <CodeMirror
          className="h-[calc(100%-3rem)]"
          extensions={[myTheme, autocompletion({ override: [myCompletions] })]}
          value={plan}
          onChange={(value) => setPlan(value)}
        />
        <Button onClick={handleRun}>Calculate</Button>
      </div>
      <div className="grow">
        <Chart history={history} setting={chartSetting} />
      </div>
    </div>
  );
};

export default Editor;
