import { useState } from "react";
import { Badge, Button, Card, Input, SyntyrRoot } from "@syntyr/react";

export function App() {
  const [value, setValue] = useState(0);

  return (
    <SyntyrRoot theme="studio" style={{ padding: "2rem" }}>
      <main>
        <Card>
          <Badge>React/Vite</Badge>
          <h1 className="syn-heading">Operations</h1>
          <p>Presentation is Syntyr CSS; counter behavior belongs to React.</p>
          <label className="syn-label" htmlFor="project-name">Project</label>
          <Input id="project-name" name="project" placeholder="Project name" />
          <Button variant="primary" onClick={() => setValue((n) => n + 1)}>
            Count: {value}
          </Button>
        </Card>
      </main>
    </SyntyrRoot>
  );
}
