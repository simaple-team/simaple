/* eslint-disable */
/**
 * This file was automatically generated by json-schema-to-typescript.
 * DO NOT MODIFY IT BY HAND. Instead, modify the source JSONSchema file,
 * and run json-schema-to-typescript to regenerate this file.
 */

export type Id = string;
export type Name = string;
export type Name1 = string;

/**
 * Component is compact bundle of state-action.
 * Component provides state and it's handler - a "reducer" which instance method decorated by @reducer_method.
 *
 * "Primary Component" is passive-component. This only listen actions and change its state.
 * "Active Component" may impact to other components. This side-effects are called as "EventHandler".
 * EventHandlers, will require target components, can be generated by install(*args) or manually created.
 *
 * Component는 연관된 상태-변화 메서드의 집합입니다.
 * 모든 reducer는 다음과 같은 형태를 준수해야 합니다.
 * (payload, ...states) => (states, optional[list[event]])
 *
 * Component는 어떠한 상태도 가지지 않는 순수-함수로서 기능해야만 합니다.
 */
export interface Component {
  id: Id;
  name: Name;
  binds?: Binds;
  [k: string]: unknown;
}
export interface ListeningActions {
  [k: string]: string | StaticPayloadReducerInfo;
}
export interface StaticPayloadReducerInfo {
  name: Name1;
  payload: Payload;
  [k: string]: unknown;
}
export interface Payload {
  [k: string]: unknown;
}
export interface Binds {
  [k: string]: string;
}
