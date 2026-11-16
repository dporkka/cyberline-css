import { useRef, useState } from "react";
import { Menu } from "@base-ui/react/menu";
import { Dialog } from "@base-ui/react/dialog";
import { Select } from "@base-ui/react/select";
import { Switch } from "@base-ui/react/switch";
import { Tabs } from "@base-ui/react/tabs";

const formats = [{ label: "Static", value: "static" }, { label: "Digital", value: "digital" }];

export default function App() {
  const portalRef = useRef<HTMLDivElement>(null);
  const [action, setAction] = useState("No action selected");

  return (
    <main className="syn-root syn-shell" data-syn-theme="studio" style={{ paddingBlock: "2rem" }}>
      <h1>Syntyr / Base UI adapter</h1>
      <p className="syn-lede">Base UI owns keyboard, focus and state; Syntyr owns CSS.</p>
      <section className="syn-panel" aria-label="Actions" style={{ marginBlock: "1rem" }}>
        <Menu.Root>
          <Menu.Trigger className="syn-base-trigger">Actions</Menu.Trigger>
          <Menu.Portal container={portalRef}>
            <Menu.Positioner sideOffset={6} align="start">
              <Menu.Popup className="syn-base-popup">
                <Menu.Item className="syn-base-item" onClick={() => setAction("Reviewed")}>Review</Menu.Item>
                <Menu.Separator className="syn-base-separator" />
                <Menu.Item className="syn-base-item" disabled>Delete (unavailable)</Menu.Item>
              </Menu.Popup>
            </Menu.Positioner>
          </Menu.Portal>
        </Menu.Root>
        <p data-testid="action-state" aria-live="polite">{action}</p>
      </section>
      <section className="syn-panel" aria-label="Settings" style={{ marginBlock: "1rem" }}>
        <Dialog.Root>
          <Dialog.Trigger className="syn-base-trigger">Open settings</Dialog.Trigger>
          <Dialog.Portal className="syn-base-dialog-viewport" container={portalRef}>
            <Dialog.Backdrop className="syn-base-backdrop" />
            <Dialog.Popup className="syn-base-popup syn-base-dialog">
              <Dialog.Title className="syn-base-dialog-title">Settings</Dialog.Title>
              <Dialog.Description className="syn-base-dialog-description">
                This is a local interaction demonstration.
              </Dialog.Description>
              <Dialog.Close className="syn-base-trigger">Close settings</Dialog.Close>
            </Dialog.Popup>
          </Dialog.Portal>
        </Dialog.Root>
      </section>
      <section className="syn-panel" aria-label="Selection" style={{ marginBlock: "1rem" }}>
        <Select.Root defaultValue="static" items={formats}>
          <Select.Trigger aria-label="Advertising format" className="syn-base-trigger">
            <Select.Value />
            <Select.Icon aria-hidden="true">⌄</Select.Icon>
          </Select.Trigger>
          <Select.Portal container={portalRef}>
            <Select.Positioner sideOffset={6} alignItemWithTrigger={false}>
              <Select.Popup className="syn-base-popup">
                <Select.List>
                  <Select.Item className="syn-base-item" value="static"><Select.ItemText>Static</Select.ItemText></Select.Item>
                  <Select.Item className="syn-base-item" value="digital"><Select.ItemText>Digital</Select.ItemText></Select.Item>
                </Select.List>
              </Select.Popup>
            </Select.Positioner>
          </Select.Portal>
        </Select.Root>
      </section>
      <section className="syn-panel" aria-label="Notifications" style={{ marginBlock: "1rem" }}>
        <label style={{ display: "inline-flex", alignItems: "center", gap: ".5rem" }}>
          <Switch.Root className="syn-base-switch" defaultChecked={false}>
            <Switch.Thumb className="syn-base-switch-thumb" />
          </Switch.Root>
          Notifications
        </label>
      </section>
      <section className="syn-panel" aria-label="Workspace panels" style={{ marginBlock: "1rem" }}>
        <Tabs.Root defaultValue="overview">
          <Tabs.List className="syn-base-tabs-list">
            <Tabs.Tab className="syn-base-tab" value="overview">Overview</Tabs.Tab>
            <Tabs.Tab className="syn-base-tab" value="activity">Activity</Tabs.Tab>
          </Tabs.List>
          <Tabs.Panel className="syn-base-tabs-panel" value="overview">Overview panel</Tabs.Panel>
          <Tabs.Panel className="syn-base-tabs-panel" value="activity">Activity panel</Tabs.Panel>
        </Tabs.Root>
      </section>
      <div ref={portalRef} data-testid="syntyr-portal-root" />
    </main>
  );
}
