export interface Validity {
  name: string;
  id: string;
  time_left: number;
  cooldown_duration: number;
  valid: boolean;
  stack: number | null;
}
