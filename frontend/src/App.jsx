import { useCallback, useEffect, useReducer, useState } from "react";
import { Panel, PanelGroup, PanelResizeHandle } from "react-resizable-panels";
import useWebSocket, { ReadyState } from "react-use-websocket";
import { ProgressBar } from "@blueprintjs/core";

import Chat from "./components/Chat.jsx";
import Plan from "./components/Plan.jsx";
import { InteractionType, MsgType, Status } from "./utils/constants.js";
import { time } from "./utils/helpers.js";
import { AppContext } from "./AppContext.jsx";
import { chatReducer, initialChatState } from "./reducers.jsx";
import { usePlanStore } from "./store.jsx";

export default function App() {
  const [sessionId, setSessionId] = useState(null);
  const [agentRegistry, setAgentRegistry] = useState(null);

  const [chatLoading, setChatLoading] = useState(false);
  const [planLoading, setPlanLoading] = useState(false);

  const [chat, dispatchChat] = useReducer(chatReducer, initialChatState);
  const setPlanLayout = usePlanStore((state) => state.setPlanLayout);
  const initializePlan = usePlanStore((state) => state.initializePlan);

  // function to start or reset a session
  const startSession = useCallback(async () => {
    try {
      const response = await fetch("http://localhost:8000/start-session");
      const data = await response.json();
      setSessionId(data.session_id);
      console.log(`[${time()}] Session started:`, data.session_id);
    } catch (error) {
      console.log(`[${time()}] Error starting session:`, error);
    }
  }, []);

  // function to fetch agent registry
  const getAgentRegistry = async () => {
    try {
      const response = await fetch("http://localhost:8000/agent-registry");
      const data = await response.json();
      const agentNames = data.agent_registry.map((d) => d.agent_name);
      const agentDefaultConfigs = data.agent_registry.reduce((acc, d) => {
        acc[d.agent_name] = d.default_config;
        return acc;
      }, {});
      setAgentRegistry({ names: agentNames, configs: agentDefaultConfigs });
      console.log(`[${time()}] Registry fetched:`, data.agent_registry);
    } catch (error) {
      console.log(`[${time()}] Error fetching agent registry:`, error);
    }
  };

  // fetch agent registry on mount
  useEffect(() => {
    getAgentRegistry();
  }, []);

  // start session on mount
  useEffect(() => {
    startSession();
  }, [startSession]);

  // websocket setup
  const socketUrl = sessionId ? `ws://localhost:8000/ws/${sessionId}` : null;
  const { sendJsonMessage, lastJsonMessage, readyState } = useWebSocket(
    socketUrl,
    { shouldReconnect: () => true, reconnectAttempts: 10 }
  );

  // send connection status
  useEffect(() => {
    const connectionState = {
      [ReadyState.CONNECTING]: "Connecting",
      [ReadyState.OPEN]: "Open",
      [ReadyState.CLOSING]: "Closing",
      [ReadyState.CLOSED]: "Closed",
      [ReadyState.UNINSTANTIATED]: "Uninstantiated",
    }[readyState];
    console.log(`[${time()}] Connection state changed:`, connectionState);
    sendJsonMessage({
      type: MsgType.CONNECTION,
      data: { state: connectionState },
    });
  }, [readyState, sendJsonMessage]);

  // receive data
  useEffect(() => {
    if (!lastJsonMessage) return;

    if (readyState === ReadyState.CLOSED || readyState === ReadyState.CLOSING) {
      console.log(`[${time()}] WebSocket closed, ignoring received messages.`);
      return; // Stop processing messages if WebSocket is closed
    }

    switch (lastJsonMessage.type) {
      case MsgType.STATUS:
        if (lastJsonMessage.data.status == Status.STARTING && [MsgType.PLAN, MsgType.EXECUTE].includes(lastJsonMessage.data.action)) {
          setPlanLoading(true);
        }
        if (lastJsonMessage.data.status == Status.FINISHED) {
          setPlanLoading(false);
        }
        console.log(
          `[${time()}] -- ${lastJsonMessage.data.action}:`,
          lastJsonMessage.data.status
        );
        break;
      case MsgType.CHAT:
        // setMessages(lastJsonMessage.data.chat_history);
        // setMessages([lastJsonMessage.data.system_response]);
        // addMessage(lastJsonMessage.data.system_response);
        dispatchChat({
          type: "ADD_SYSTEM_RESPONSE",
          payload: lastJsonMessage.data.system_response,
        });
        setChatLoading(false);
        console.log(
          `[${time()}] Chat updated:`,
          lastJsonMessage.data,
          lastJsonMessage.data.system_response
        );
        break;
      case MsgType.PLAN:
        setPlanLayout(lastJsonMessage.data.plan);
        setPlanLoading(false);
        console.log(`[${time()}] Plan updated:`, lastJsonMessage.data.plan);
        break;
      default:
        console.log(`[${time()}] Msg received:`, lastJsonMessage);
    }
  }, [lastJsonMessage]);

  // chat view buttons
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
    sendJsonMessage({ type: MsgType.CHAT, data: msg });
  };

  const requestReset = async () => {
    console.log(`[${time()}] Reset requested`);
    dispatchChat({ type: "CLEAR_CHAT" });

    setPlanLoading(true);
    sendJsonMessage({ type: MsgType.RESET, data: {} });
    initializePlan();
    setPlanLoading(false);
  };

  // plan view buttons
  const requestExecute = async (mode, node_id = null) => {
    console.log(`[${time()}] Execution requested:`, mode, node_id);
    setPlanLoading(true);
    // temporary
    // const { nodes, edges } = usePlanStore.getState();
    // sendJsonMessage({ type: MsgType.PLAN, data: { nodes, edges } });
    // temporary
    sendJsonMessage({
      type: MsgType.EXECUTE,
      data: { mode: mode, node_id: node_id },
    });
  };

  const requestFixPlan = async () => {
    console.log(`[${time()}] Plan fix requested`);
    const { id, query, timestamp, nodes, edges } = usePlanStore.getState();
    setPlanLoading(true);
    sendJsonMessage({
      type: MsgType.INTERACTION,
      data: { interaction: InteractionType.FIX_PLAN, plan: { id, query, timestamp, nodes, edges } },
    });
  };

  const requestRePlan = async () => {
    console.log(`[${time()}] Re-plan requested`);
    setPlanLoading(true);
    sendJsonMessage({
      type: MsgType.INTERACTION,
      data: { interaction: InteractionType.REPLAN },
    });
  };

  // direct plan manipulation
  const sendInteraction = (ixData) => {
    console.log(`[${time()}] Interaction sent: ${ixData.interaction}`);
    const { id, query, timestamp, nodes, edges } = usePlanStore.getState();
    sendJsonMessage({
      type: MsgType.INTERACTION,
      data: { ...ixData, plan: { id, query, timestamp, nodes, edges } },
      // data: { ...ixData },
    });
  };

  const sendPlan = async (nodes, edges) => {
    // async function sendPlan(nodes, edges) {
    console.log(`[${time()}] Updated plan sent`);
    sendJsonMessage({ type: MsgType.PLAN, data: { nodes, edges } });
  };

  return (
    <AppContext.Provider
      value={{
        rePlan: requestRePlan,
        fixPlan: requestFixPlan,
        executeNode: requestExecute,
        sendInteraction: sendInteraction,
        sendPlan: sendPlan,
        agentRegistry: agentRegistry,
      }}
    >
      <PanelGroup direction="horizontal">
        <Panel className="panel" defaultSize={35} minSize={20}>
          <Chat
            messages={chat.messages}
            isLoading={chatLoading}
            clearChat={requestReset}
            sendMessage={sendMessage}
          />
        </Panel>
        <PanelResizeHandle className="panelHandle" />
        <Panel className="panel" collapsible minSize={30}>
          {planLoading && <ProgressBar value={planLoading} />}
          <Plan />
        </Panel>
      </PanelGroup>
    </AppContext.Provider>
  );
}
