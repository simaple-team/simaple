import { styleTags, tags as t } from "@lezer/highlight";

export const simapleHighlighting = styleTags({
  QuotedString: t.string,
  Number: t.number,
  Repetition: t.operator,
  CastStatement: t.keyword,
  ElapseStatement: t.keyword,
  ResolveStatement: t.keyword,
  KeydownStopStatement: t.keyword,
  Comment: t.lineComment,
});
