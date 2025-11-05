import { useEffect, useRef, useState } from "react";
import { Button, NonIdealState, TextArea, Tooltip } from "@blueprintjs/core";

import MessageList from "./MessageList";

export default function Chat({ clearChat, sendMessage, messages, isLoading }) {
  const [message, setMessage] = useState("");
  const messageListContainer = useRef(null);

  const handleSend = () => {
    if (message.trim()) {
      sendMessage(message);
      setMessage("");
    }
  };

  // ref: https://dev.to/martinez/real-scroll-for-a-chat-application-22co
  const Scroll = () => {
    const { offsetHeight, scrollHeight, scrollTop } =
      messageListContainer.current;
    if (scrollHeight <= scrollTop + offsetHeight + 100) {
      messageListContainer.current?.scrollTo(0, scrollHeight);
    }
  };

  useEffect(() => {
    Scroll();
  }, [messages]);

  return (
    <>
      <div className="messageListContainer" ref={messageListContainer}>
        {messages.length > 0 ? (
          <MessageList messages={messages} isLoading={isLoading} />
        ) : (
          <NonIdealState icon="chat" title="No messages"
            description={
              <>
                Try asking math reasoning questions. Examples:
                <br />
                <ul style={{ textAlign: "left" }}>
                  <li>
                    “Sophie buys chocolate cupcakes for $2 each and vanilla cupcakes for $1.50 each. She has $30 and buys 5 more chocolate cupcakes than vanilla ones. How many chocolate and vanilla cupcakes does Sophie buy?”
                  </li>
                  <li>
                    “Liam buys 3 books for $12 each and 2 notebooks for $3 each. He then gets a 10% discount on his total purchase. How much does Liam pay in total after the discount?”
                  </li>
                </ul>
              </>
            }
          />
        )}
      </div>
      <div className="messageInputContainer">
        <Tooltip content="Clear everything" placement="top-start">
          <Button text="Reset" onClick={clearChat} style={{ height: "100%" }} />
        </Tooltip>
        <TextArea fill placeholder="Enter text..."
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter" && !(e.altKey || e.ctrlKey || e.shiftKey || e.metaKey) && !isLoading) {
              e.preventDefault();
              handleSend();
            }
          }}
        />
        <Button intent="primary" icon="send-message"
          disabled={!message || isLoading}
          onClick={handleSend}
        />
      </div>
    </>
  );
}
