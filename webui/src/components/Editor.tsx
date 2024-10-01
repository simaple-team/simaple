import { Button } from "@/components/ui/button";
import {
  autocompletion,
  Completion,
  CompletionContext,
  CompletionResult,
} from "@codemirror/autocomplete";
import { yamlFrontmatter } from "@codemirror/lang-yaml";
import { LanguageSupport, LRLanguage, syntaxTree } from "@codemirror/language";
import { Diagnostic, linter } from "@codemirror/lint";
import { styleTags } from "@lezer/highlight";
import CodeMirror, {
  EditorView,
  Extension,
  keymap,
} from "@uiw/react-codemirror";
import { Loader2 } from "lucide-react";
import { useCallback, useMemo, useState } from "react";
import { useWorkspace } from "../hooks/useWorkspace";
import { parser } from "../parser";
import CreateBaselineFileDialog from "./CreateBaselineFileDialog";
import ErrorDialog from "./ErrorDialog";

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

  function getCompletions(context: CompletionContext): CompletionResult | null {
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
        { label: "RESOLVE", type: "keyword" },
        { label: "KEYDOWNEND", type: "keyword" },
      ],
      validFor: /^([가-힣]*|\w*)$/,
    };
  }

  return getCompletions;
}

function skillNameLinter(skillNames: string[]) {
  return linter((view) => {
    if (skillNames.length === 0) {
      return [];
    }

    const diagnostics: Diagnostic[] = [];
    syntaxTree(view.state)
      .cursor()
      .iterate((node) => {
        if (node.name === "QuotedString") {
          const skillName = view.state.doc
            .slice(node.from, node.to)
            .toString()
            .replace(/"/g, "");

          if (!skillNames.includes(skillName)) {
            diagnostics.push({
              from: node.from,
              to: node.to,
              severity: "error",
              message: "Wrong skill name",
            });
          }
        }
      });
    return diagnostics;
  });
}

const myTheme = EditorView.theme({
  "&": { height: "100%" },
  ".cm-scroller": { overflow: "auto" },
});

export function Editor() {
  const [isRunning, setIsRunning] = useState(false);
  const { plan, setPlan, skillNames, run, errorMessage, clearErrorMessage } =
    useWorkspace();

  const handleRun = useCallback(async () => {
    if (isRunning) {
      return;
    }

    setIsRunning(true);
    await run();
    setIsRunning(false);
  }, [isRunning, run]);

  const extensions: Extension[] = useMemo(
    () => [
      myTheme,
      keymap.of([
        {
          key: "Shift-Enter",
          run: () => {
            handleRun();
            return true;
          },
        },
      ]),
      languageSupport(),
      skillNameLinter(skillNames),
      autocompletion({ override: [createCompletion(skillNames)] }),
    ],
    [skillNames, handleRun],
  );

  return (
    <div className="flex h-full flex-col shrink-0 w-[480px] gap-2 border-r border-border/40">
      <CodeMirror
        className="h-[calc(100%-4rem)]"
        basicSetup={{ closeBrackets: false }}
        extensions={extensions}
        value={plan}
        onChange={(value) => setPlan(value)}
      />
      <div className="flex gap-2 p-2">
        <CreateBaselineFileDialog>
          <Button variant="outline">새 파일</Button>
        </CreateBaselineFileDialog>
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
            "계산 (Shift + Enter)"
          )}
        </Button>
        <ErrorDialog
          open={!!errorMessage}
          onOpenChange={(open) => (open ? null : clearErrorMessage())}
        >
          {errorMessage}
        </ErrorDialog>
      </div>
    </div>
  );
}
