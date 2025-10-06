// src/components/ChartViewer.tsx
import React, { useEffect, useState } from "react";
import { VegaEmbed } from "react-vega";

type Props = {
  document: string;
  userRequest: string;
};

export default function ChartViewer({ document, userRequest }: Props) {
  const [spec, setSpec] = useState<any | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function fetchSpec() {
      setError(null);
      setSpec(null);
      try {
        const resp = await fetch("/api/generate_chart", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ document, user_request: userRequest }),
        });
        const json = await resp.json();
        // Esperamos { vega_lite: { ... } }
        setSpec(json.vega_lite);
      } catch (e: any) {
        setError(e.message ?? String(e));
      }
    }
    fetchSpec();
  }, [document, userRequest]);

  if (error) return <div>Error: {error}</div>;
  if (!spec) return <div>Generando gráfico…</div>;

  return (
    <div>
      <VegaEmbed spec={spec} />
    </div>
  );
}
