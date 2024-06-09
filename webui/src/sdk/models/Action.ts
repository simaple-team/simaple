export interface Action {
  name: string;
  method: string;
  payload?: number | string | Record<string, any>;
}
