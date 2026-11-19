import { useState } from "react"
import { Button } from "@/components/ui/button"

export function App() {
  const [count, setCount] = useState(0)

  return (
    <div id="host" className="p-5">
      <p>Host tokens remain separate from the Syntyr opt-in region.</p>
      <main className="syn-root syn-shadcn mt-6 min-h-[26rem] p-6 md:p-10" data-syn-theme="studio">
        <div className="mx-auto max-w-3xl space-y-5">
          <h1 className="text-2xl font-semibold">Actual shadcn/ui + Syntyr</h1>
          <section className="rounded-lg border border-border bg-card p-6 text-card-foreground">
            <h2 className="text-xl">Studio palette</h2>
            <p className="text-muted-foreground">Generated Radix-backed shadcn button with inherited Syntyr semantic colors.</p>
            <div className="mt-4 flex flex-wrap gap-3">
              <Button id="react-action" onClick={() => setCount((value) => value + 1)}>
                Increment {count}
              </Button>
              <Button asChild variant="outline">
                <a id="aschild-link" href="#details">View details</a>
              </Button>
              <Button disabled id="disabled-action">Unavailable</Button>
            </div>
          </section>
          <section data-syn-theme="noir" className="rounded-lg border border-border bg-card p-6 text-card-foreground">
            <h2 className="text-xl" id="details">Nested Noir palette</h2>
            <Button id="noir-action">Noir action</Button>
          </section>
        </div>
      </main>
    </div>
  )
}

export default App
