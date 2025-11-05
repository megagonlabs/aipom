import { useContext } from "react";
import { ReadyState } from "react-use-websocket";

import { AppContext } from "../AppContext";

export default function ConnectionIndicator() {
  const { readyState } = useContext(AppContext);
  const isConnected = readyState === ReadyState.OPEN;

  return (
    !isConnected && (
      <div className="connection-indicator">
        <div
          className="connection-indicator-light"
          style={{ backgroundColor: "red" }}
        />
        <span>Disconnected</span>
      </div>
    )
  );
}
