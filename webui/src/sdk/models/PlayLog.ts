import { Stat } from "./Stat";
import { Event } from "./Event";
import { Validity } from "./Validity";
import { Running } from "./Running";
import { Action } from "./Action";
import { Keydown } from "./Keydown";

export interface PlayLog {
  events: Event[];
  index: number;
  validity_view: Record<string, Validity>;
  running_view: Record<string, Running>;
  keydown_view: Record<string, Keydown>;
  buff_view: Stat;
  damage: number;
  damages: [string, number][];
  clock: number;
  delay: number;
  action: Action;
  checkpoint: Record<string, string>;
  previous_hash: string;
  hash: string;
}
