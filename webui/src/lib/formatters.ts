export function damageFormatter(value: number) {
  if (value < 10000) return value.toFixed(0);

  if (value < 100000000) return (value / 10000).toFixed(2) + "만";

  if (value < 1000000000000) return (value / 100000000).toFixed(2) + "억";

  return (value / 1000000000000).toFixed(2) + "조";
}

export function percentageFormatter(value: number) {
  return (value * 100).toFixed(2) + "%";
}

export function secFormatter(valueMs: number) {
  return (valueMs / 1000).toFixed(2) + "초";
}

const intlTimesFormatter = Intl.NumberFormat(undefined, {
  maximumFractionDigits: 2,
  minimumFractionDigits: 0,
});
export function timesFormatter(value: number) {
  return intlTimesFormatter.format(value) + "회";
}
