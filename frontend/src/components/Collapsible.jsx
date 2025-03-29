import { useState } from "react";
import { Button, Collapse } from "@blueprintjs/core";

export function Collapsible(props) {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <div>
      <Button
        icon="cog"
        // intent="primary"
        variant="minimal"
        aria-label="cog"
        onClick={() => setIsOpen(!isOpen)}
      />
      <Collapse isOpen={isOpen} keepChildrenMounted={true}>
        {props.children}
      </Collapse>
    </div>
  );
}
