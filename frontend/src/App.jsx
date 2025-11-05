import { useEffect, useReducer, useState } from "react";
import { Panel, PanelGroup, PanelResizeHandle } from "react-resizable-panels";
import { ReadyState } from "react-use-websocket";
import { ProgressBar } from "@blueprintjs/core";

import Chat from "./components/Chat";
import ConnectionIndicator from "./components/ConnectionIndicator";
import Plan from "./components/Plan";
import { useAppWebSocket } from "./hooks/useAppWebSocket";
import { useWebSocketActions } from "./hooks/useWebSocketActions";
import { chatReducer, initialChatState } from "./store/chatReducer";
import { usePlanStore } from "./store/planStore";
import { MsgType, Status } from "./utils/constants";
import { time } from "./utils/helpers";
import { AppContext } from "./AppContext";
import config from "./config";

export default function App() {
  const [sessionId, setSessionId] = useState(null);
  const [agentRegistry, setAgentRegistry] = useState(null);

  const [chatLoading, setChatLoading] = useState(false);
  const [planLoading, setPlanLoading] = useState(false);

  const [chat, dispatchChat] = useReducer(chatReducer, initialChatState);
  const setPlanLayout = usePlanStore((state) => state.setPlanLayout);

  // start session on mount
  useEffect(() => {
    // function to start or reset a session
    const startSession = async () => {
      try {
        const response = await fetch(`${config.backendBaseUrl}/start-session`, {
          method: "POST",
        });
        const data = await response.json();
        setSessionId(data.session_id);
        console.log(`[${time()}] Session started:`, data.session_id);
      } catch (error) {
        console.log(`[${time()}] Error starting session:`, error);
      }
    };

    startSession();
  }, []);

  // fetch agent registry on mount
  useEffect(() => {
    // function to fetch agent registry
    const getAgentRegistry = async () => {
      try {
        const response = await fetch(`${config.backendBaseUrl}/agent-registry`);
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

    getAgentRegistry();
  }, []);

  const { sendJsonMessage, lastJsonMessage, readyState } =
    useAppWebSocket(sessionId);

  const {
    sendMessage,
    requestReset,
    requestExecute,
    requestFixPlan,
    requestRePlan,
    sendInteraction,
    sendPlan,
  } = useWebSocketActions({
    chat,
    dispatchChat,
    setChatLoading,
    setPlanLoading,
    sendJsonMessage,
    readyState,
  });

  // receive data
  useEffect(() => {
    if (!lastJsonMessage) return;

    if (readyState === ReadyState.CLOSED || readyState === ReadyState.CLOSING) {
      console.log(`[${time()}] WebSocket closed, ignoring received messages.`);
      return; // Stop processing messages if WebSocket is closed
    }

    switch (lastJsonMessage.type) {
      case MsgType.STATUS:
        if (
          lastJsonMessage.data.status == Status.STARTING &&
          [MsgType.PLAN, MsgType.EXECUTE].includes(lastJsonMessage.data.action)
        ) {
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
        if (lastJsonMessage.data.chat_history) {
          dispatchChat({
            type: "SET_CHAT_HISTORY",
            payload: lastJsonMessage.data.chat_history,
          });
        } else {
          dispatchChat({
            type: "ADD_SYSTEM_RESPONSE",
            payload: lastJsonMessage.data.system_response,
          });
        }
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

  return (
    <AppContext.Provider
      value={{
        rePlan: requestRePlan,
        fixPlan: requestFixPlan,
        executeNode: requestExecute,
        sendInteraction: sendInteraction,
        sendPlan: sendPlan,
        agentRegistry: agentRegistry,
        readyState: readyState,
      }}
    >
      <PanelGroup direction="horizontal">
        <Panel className="panel" defaultSize={35} minSize={20}>
          <ConnectionIndicator />
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
