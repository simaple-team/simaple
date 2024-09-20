import { Button } from "@/components/ui/button";
import {
  autocompletion,
  Completion,
  CompletionContext,
  CompletionResult,
} from "@codemirror/autocomplete";
import { yamlFrontmatter } from "@codemirror/lang-yaml";
import { LanguageSupport, LRLanguage, syntaxTree } from "@codemirror/language";
import { styleTags } from "@lezer/highlight";
import CodeMirror, { EditorView, keymap } from "@uiw/react-codemirror";
import { Loader2 } from "lucide-react";
import * as React from "react";
import { useWorkspace } from "../hooks/useWorkspace";
import { parser } from "../parser";
import CreateBaselineSimulatorDialog from "./CreateBaselineSimulatorDialog";

const parserWithMetadata = parser.configure({
  props: [styleTags({})],
});

const simapleLanguage = LRLanguage.define({
  parser: parserWithMetadata,
});

function languageSupport() {
  return yamlFrontmatter({
    content: new LanguageSupport(simapleLanguage),
  });
}

function createCompletion(skillNames: string[]) {
  const completions: Completion[] = skillNames.map((name) => ({
    label: name,
    type: "constant",
  }));

  function myCompletions(context: CompletionContext): CompletionResult | null {
    const before = context.matchBefore(/([가-힣]+|\w+)/);
    const quotedBefore = context.matchBefore(/"([가-힣]*|\w*)/);

    // If completion wasn't explicitly started and there
    // is no word before the cursor, don't open completions.
    if (!context.explicit && !before && !quotedBefore) return null;

    if (quotedBefore) {
      const nodeBefore = syntaxTree(context.state).resolveInner(
        context.pos,
        -1,
      );
      if (nodeBefore?.type.name === "QuotedString") {
        return null;
      }

      return {
        from: quotedBefore ? quotedBefore.from + 1 : context.pos,
        options: completions.map((completion) => ({
          ...completion,
          apply: `${completion.label}"`,
        })),
        validFor: /^([가-힣]*|\w*)$/,
      };
    }

    return {
      from: before ? before.from : context.pos,
      options: [
        ...completions.map((completion) => ({
          ...completion,
          apply: `"${completion.label}"`,
        })),
        { label: "CAST", type: "keyword" },
        { label: "ELAPSE", type: "keyword" },
      ],
      validFor: /^([가-힣]*|\w*)$/,
    };
  }

  return myCompletions;
}

const myTheme = EditorView.theme({
  "&": { height: "100%" },
  ".cm-scroller": { overflow: "auto" },
});

export function Editor() {
  const [isRunning, setIsRunning] = React.useState(false);
  const { plan, setPlan, skillNames, runAsync } = useWorkspace();

  const myCompletions = React.useMemo(
    () => createCompletion(skillNames),
    [skillNames],
  );

  async function handleRun() {
    if (isRunning) {
      return;
    }

    setIsRunning(true);
    await runAsync();
    setIsRunning(false);
  }

  function handleHotkeyRun(): boolean {
    handleRun();
    return true;
  }

  return (
    <div className="flex h-full flex-col shrink-0 w-[520px] gap-2 border-r border-border/40">
      <CodeMirror
        className="h-[calc(100%-4rem)]"
        basicSetup={{ closeBrackets: false }}
        extensions={[
          myTheme,
          keymap.of([
            {
              key: "Shift-Enter",
              run: handleHotkeyRun,
            },
          ]),
          languageSupport(),
          autocompletion({ override: [myCompletions] }),
        ]}
        value={plan}
        onChange={(value) => setPlan(value)}
      />
      <div className="flex gap-2 p-2">
        <CreateBaselineSimulatorDialog>
          <Button variant="outline">새 파일</Button>
        </CreateBaselineSimulatorDialog>
        <Button
          disabled={isRunning || plan.trim().length === 0}
          onClick={handleRun}
          className="grow"
        >
          {isRunning ? (
            <>
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              계산 중...
            </>
          ) : (
            "계산"
          )}
        </Button>
      </div>
    </div>
  );
}
