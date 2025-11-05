import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { FocusStyleManager } from "@blueprintjs/core";

import App from "./App";

import "@blueprintjs/core/lib/css/blueprint.css";
import "normalize.css/normalize.css";
import "./App.css";

FocusStyleManager.onlyShowFocusOnTabs();

const root = createRoot(document.getElementById("root"));
root.render(
  <StrictMode>
    <App />
  </StrictMode>
);
