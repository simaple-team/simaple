export function damageFormatter(value: number) {
  if (value < 10000) return value.toFixed(0);

  if (value < 100000000) return (value / 10000).toFixed(2) + "만";

  if (value < 1000000000000) return (value / 100000000).toFixed(2) + "억";

  return (value / 1000000000000).toFixed(2) + "조";
}

export function clockFormatter(value: number) {
  return value + "ms";
}

export function percentageFormatter(value: number) {
  return (value * 100).toFixed(2) + "%";
}

export function secFormatter(valueMs: number) {
  return (valueMs / 1000).toFixed(2) + "초";
}
