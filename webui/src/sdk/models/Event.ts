export interface Event {
  name: string;
  method: string;
  tag?: string;
  handler?: string;
  payload: any;
}
