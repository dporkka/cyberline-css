import React from "react";
import { createRoot } from "react-dom/client";
import App from "./App";
import "../../../dist/syntyr.core.css";
import "../../../integrations/base-ui/states.css";

createRoot(document.getElementById("root")!).render(
  <React.StrictMode><App /></React.StrictMode>
);
