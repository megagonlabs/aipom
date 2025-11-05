import { v4 as uuidv4 } from "uuid";

export const time = () => {
  return new Date().toLocaleTimeString("eo", { hour12: false });
};

export const uuid = () => {
  return uuidv4().slice(0, 8);
};
