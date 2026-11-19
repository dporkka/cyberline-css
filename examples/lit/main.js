import "./status-panel.js";
import "./shadow-signal.js";

const eventOutput = document.querySelector("#event-output");
document.addEventListener("syn-demo-status-change", (event) => {
  eventOutput.textContent =
    `${event.detail.service}: ${event.detail.online ? "online" : "offline"} (light DOM event)`;
});
document.addEventListener("syn-demo-signal-change", (event) => {
  eventOutput.textContent =
    `Relay gateway: ${event.detail.active ? "active" : "standby"} (composed shadow event)`;
});
