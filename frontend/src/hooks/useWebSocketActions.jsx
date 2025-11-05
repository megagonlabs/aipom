import { useEffect, useRef } from "react";
import { ReadyState } from "react-use-websocket";

import { usePlanStore } from "../store/planStore";
import { InteractionType, MsgType } from "../utils/constants";
import { time } from "../utils/helpers";

export const useWebSocketActions = ({
  chat,
  dispatchChat,
  setChatLoading,
  setPlanLoading,
  sendJsonMessage,
  readyState,
}) => {
  const initializePlan = usePlanStore((state) => state.initializePlan);

  const prevReadyState = useRef(null);
  const ReadyStateMap = {
    [ReadyState.CONNECTING]: "Connecting",
    [ReadyState.OPEN]: "Open",
    [ReadyState.CLOSING]: "Closing",
    [ReadyState.CLOSED]: "Closed",
    [ReadyState.UNINSTANTIATED]: "Uninstantiated",
  };

  // send connection status
  useEffect(() => {
    if (prevReadyState.current === readyState) return;
    prevReadyState.current = readyState;

    const connectionState = ReadyStateMap[readyState] || "Unknown";
    console.log(`[${time()}] Connection state changed:`, connectionState);
    sendJsonMessage({
      type: MsgType.CONNECTION,
      data: { state: connectionState },
      timestamp: Date.now(),
    });
  }, [readyState, sendJsonMessage]);

  // send chat message
  const sendMessage = async (message) => {
    const msg = {
      id: chat.nextId,
      role: "user",
      content: message,
      timestamp: Date.now(),
    };
    dispatchChat({ type: "ADD_USER_MESSAGE", payload: msg });

    setChatLoading(true);
    setPlanLoading(true);
    sendJsonMessage({ type: MsgType.CHAT, data: msg, timestamp: Date.now() });
  };

  // send direct manipulation
  const sendInteraction = async (ixData) => {
    console.log(`[${time()}] Interaction sent: ${ixData.interaction}`);
    const { id, query, timestamp, nodes, edges } = usePlanStore.getState();
    sendJsonMessage({
      type: MsgType.INTERACTION,
      data: { ...ixData, plan: { id, query, timestamp, nodes, edges } },
      timestamp: Date.now(),
    });
  };

  // send plan
  const sendPlan = async (nodes, edges) => {
    console.log(`[${time()}] Updated plan sent`);
    sendJsonMessage({
      type: MsgType.PLAN,
      data: { nodes, edges },
      timestamp: Date.now(),
    });
  };

  const requestReset = async () => {
    console.log(`[${time()}] Reset requested`);
    dispatchChat({ type: "CLEAR_CHAT" });

    setPlanLoading(true);
    sendJsonMessage({ type: MsgType.RESET, data: {}, timestamp: Date.now() });
    initializePlan();
    setPlanLoading(false);
  };

  const requestExecute = async (mode, node_id = null) => {
    console.log(`[${time()}] Execution requested:`, mode, node_id);
    setPlanLoading(true);
    sendJsonMessage({
      type: MsgType.EXECUTE,
      data: { mode: mode, node_id: node_id },
      timestamp: Date.now(),
    });
  };

  const requestFixPlan = async () => {
    console.log(`[${time()}] Plan fix requested`);
    const { id, query, timestamp, nodes, edges } = usePlanStore.getState();
    setPlanLoading(true);
    sendJsonMessage({
      type: MsgType.INTERACTION,
      data: {
        interaction: InteractionType.FIX_PLAN,
        plan: { id, query, timestamp, nodes, edges },
        timestamp: Date.now(),
      },
    });
  };

  const requestRePlan = async () => {
    console.log(`[${time()}] Re-plan requested`);
    setPlanLoading(true);
    sendJsonMessage({
      type: MsgType.INTERACTION,
      data: { interaction: InteractionType.REPLAN },
      timestamp: Date.now(),
    });
  };

  return {
    sendMessage,
    sendInteraction,
    sendPlan,
    requestReset,
    requestExecute,
    requestFixPlan,
    requestRePlan,
  };
};
