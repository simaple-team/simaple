import { styleTags, tags as t } from "@lezer/highlight";

export const simapleHighlighting = styleTags({
  Quotedstring: t.string,
  Number: t.number,
  Repetition: t.operator,
  CastStatement: t.keyword,
  ElapseStatement: t.keyword,
});
