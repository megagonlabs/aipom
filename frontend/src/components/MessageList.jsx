import { Callout } from "@blueprintjs/core";

export default function MessageList({ messages, isLoading }) {
  const rows = [];
  messages.forEach((m, i) => {
    // if (m.role === "system") return;
    rows.push(
      <div className={"row " + (m.role === "user" ? "right" : "")} key={i}>
        <Callout className="message" compact
          icon={m.has_plan ? "tick" : null}
          intent={
            m.role === "user" ? "primary" : m.role === "system" ? "warning" : ""
          }
        >
          {m.content}
        </Callout>
      </div>
    );
  });

  return (
    <>
      {rows}
      {isLoading && (
        <div className="row" key="loading">
          <Callout className="message bp5-skeleton" compact icon={null}>
            -
          </Callout>
        </div>
      )}
    </>
  );
}
