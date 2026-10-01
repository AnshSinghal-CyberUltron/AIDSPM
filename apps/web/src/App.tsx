import { useEffect, useState } from "react";
import { Button } from "@/components/ui/button";

type SystemState = {
  installation_id: string;
  build_revision: string;
  database: string;
};

export default function App() {
  const [system, setSystem] = useState<SystemState | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    fetch("/api/v1/system")
      .then(async (response) => {
        if (!response.ok) {
          throw new Error(`system ${response.status}`);
        }
        return (await response.json()) as SystemState;
      })
      .then((body) => {
        if (!cancelled) {
          setSystem(body);
        }
      })
      .catch((reason: unknown) => {
        if (!cancelled) {
          setError(reason instanceof Error ? reason.message : "system unavailable");
        }
      });
    return () => {
      cancelled = true;
    };
  }, []);

  return (
    <main className="p-8">
      <h1 className="text-xl">AI DSPM</h1>
      <p data-testid="system-status">
        {system
          ? `database ${system.database} · ${system.installation_id}`
          : error ?? "Loading installation state"}
      </p>
      <Button type="button">Build check</Button>
    </main>
  );
}
