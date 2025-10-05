// src/views/PagX.tsx (usa el nombre de archivo que prefieras)
import * as React from "react";
import { useNavigate } from "react-router-dom";

/* ───────── Pie (pastel) interactivo en SVG ───────── */
type PieData = { label: string; value: number; color: string };

function polarToCartesian(cx: number, cy: number, r: number, angleDeg: number) {
  const rad = (Math.PI / 180) * angleDeg;
  return { x: cx + r * Math.cos(rad), y: cy + r * Math.sin(rad) };
}

function describeSlice(
  cx: number,
  cy: number,
  r: number,
  startAngle: number,
  endAngle: number
) {
  const start = polarToCartesian(cx, cy, r, startAngle);
  const end = polarToCartesian(cx, cy, r, endAngle);
  const largeArc = endAngle - startAngle <= 180 ? 0 : 1;
  return [
    `M ${cx} ${cy}`,
    `L ${start.x} ${start.y}`,
    `A ${r} ${r} 0 ${largeArc} 1 ${end.x} ${end.y}`,
    "Z",
  ].join(" ");
}

function InteractivePie({
  data,
  width = 420,
  height = 340,
  radius = 130,
  onToggle,
  selected = [],
}: {
  data: PieData[];
  width?: number;
  height?: number;
  radius?: number;
  onToggle: (index: number) => void;
  selected?: number[];
}) {
  const cx = width / 2;
  const cy = height / 2;
  const total = data.reduce((s, d) => s + d.value, 0);
  const startAngle = -90; // inicia arriba

  let cum = 0;
  const slices = data.map((d, i) => {
    const angleSpan = (d.value / total) * 360;
    const a0 = startAngle + cum;
    const a1 = a0 + angleSpan;
    cum += angleSpan;
    const mid = (a0 + a1) / 2;
    const labelPos = polarToCartesian(cx, cy, radius * 0.6, mid);

    const isSelected = selected.includes(i);
    return (
      <g key={i} style={{ cursor: "pointer" }} onClick={() => onToggle(i)}>
        <path
          d={describeSlice(cx, cy, radius, a0, a1)}
          fill={d.color}
          stroke="#fff"
          strokeWidth={isSelected ? 3 : 1.5}
          opacity={isSelected ? 1 : 0.9}
        />
        {angleSpan >= 12 && (
          <text
            x={labelPos.x}
            y={labelPos.y}
            fontSize={12}
            fontWeight={600}
            fill="#111827"
            textAnchor="middle"
            dominantBaseline="middle"
            style={{ userSelect: "none", pointerEvents: "none" }}
          >
            {d.label}
          </text>
        )}
      </g>
    );
  });

  return (
    <svg width={width} height={height} viewBox={`0 0 ${width} ${height}`}>
      {slices}
    </svg>
  );
}

/* ───────── Gráfica de barras SVG con barras clicables ───────── */
type BarItem = { name: string; value: number };

function ClickableBars({
  data,
  width = 520,
  height = 300,
  onBarClick,
}: {
  data: BarItem[];
  width?: number;
  height?: number;
  onBarClick: (index: number) => void;
}) {
  const margin = { top: 12, right: 12, bottom: 28, left: 36 };
  const plotW = width - margin.left - margin.right;
  const plotH = height - margin.top - margin.bottom;

  const max = Math.max(...data.map((d) => d.value));
  const n = data.length;
  const gap = 12;
  const band = plotW / n;
  const barW = Math.max(8, band - gap);

  const xFor = (i: number) => margin.left + i * band + (band - barW) / 2;
  const yFor = (v: number) => margin.top + plotH - (v / max) * plotH;
  const hFor = (v: number) => (v / max) * plotH;

  return (
    <svg width={width} height={height}>
      {/* Eje X (línea) */}
      <line
        x1={margin.left}
        y1={margin.top + plotH}
        x2={margin.left + plotW}
        y2={margin.top + plotH}
        stroke="#e5e7eb"
      />
      {/* Barras */}
      {data.map((d, i) => (
        <g key={i}>
          <rect
            x={xFor(i)}
            y={yFor(d.value)}
            width={barW}
            height={hFor(d.value)}
            fill="#2563EB"
            rx={6}
            style={{ cursor: "pointer" }}
            onClick={() => onBarClick(i)}
          />
          {/* Etiqueta X */}
          <text
            x={margin.left + i * band + band / 2}
            y={margin.top + plotH + 18}
            fontSize={12}
            textAnchor="middle"
            fill="#374151"
          >
            {d.name}
          </text>
        </g>
      ))}
    </svg>
  );
}

/* ───────── Página completa ───────── */
export default function PageInteractivePieBarsFixed() {
  const navigate = useNavigate();

  const pieData: PieData[] = Array.from({ length: 10 }, (_, i) => ({
    label: `Parte ${i + 1}`,
    value: 10,
    color: [
      "#2563EB",
      "#10B981",
      "#F59E0B",
      "#EF4444",
      "#06B6D4",
      "#A855F7",
      "#84CC16",
      "#F97316",
      "#0EA5E9",
      "#E11D48",
    ][i],
  }));

  // Seleccionadas (máx 3)
  const [selected, setSelected] = React.useState<number[]>([]);

  const toggleIdx = (idx: number) => {
    setSelected((prev) => {
      if (prev.includes(idx)) return prev.filter((i) => i !== idx);
      if (prev.length >= 3) return prev;
      return [...prev, idx];
    });
  };

  const textForSlice = (idx: number) => `Seleccionaste la ${pieData[idx].label}.`;

  // Barras (1 dato por categoría, ordenadas desc)
  const barData: BarItem[] = [
    { name: "NombreA", value: 9 },
    { name: "NombreB", value: 7 },
    { name: "NombreC", value: 6 },
    { name: "NombreD", value: 4 },
    { name: "NombreE", value: 2 },
  ].sort((a, b) => b.value - a.value);

  // 👇 Navega a /pag5 al hacer click en barras
  const onBarClick = (_i: number) => {
    navigate("/pag5");
  };

  return (
    <div style={styles.page}>
      {/* IZQUIERDA: 2 filas */}
      <div style={styles.left}>
        {/* Arriba: Pie interactivo */}
        <div style={styles.topLeft}>
          <h3 style={styles.title}>Pastel (10 partes)</h3>
          <InteractivePie
            data={pieData}
            width={420}
            height={340}
            radius={130}
            onToggle={toggleIdx}
            selected={selected}
          />
          <div style={styles.hint}>
            Haz click en una parte para mostrar/ocultar una caja (máx. 3).
          </div>
        </div>

        {/* Abajo: Barras clicables */}
        <div style={styles.bottomLeft}>
          <h3 style={styles.title}>Barras</h3>
          <div style={{ width: 520 }}>
            <ClickableBars data={barData} width={520} height={300} onBarClick={onBarClick} />
          </div>
        </div>
      </div>

      {/* DERECHA: 3 cajas centradas, invisibles hasta seleccionar */}
      <div style={styles.right}>
        <div style={styles.boxesWrap}>
          {[0, 1, 2].map((slot) => {
            const has = selected[slot] !== undefined;
            const idx = selected[slot];
            return (
              <div
                key={slot}
                style={{
                  ...styles.textBox,
                  opacity: has ? 1 : 0,
                  pointerEvents: has ? "auto" : "none",
                  transform: has ? "translateY(0px)" : "translateY(8px)",
                }}
                // 👇 Click en caja visible -> /pag5
                onClick={() => has && navigate("/pag5")}
              >
                <div style={styles.textBoxTitle}>
                  {has ? `Caja ${slot + 1}` : `Caja ${slot + 1} (oculta)`}
                </div>
                <div style={styles.textBoxBody}>
                  {has
                    ? textForSlice(idx)
                    : "Selecciona una parte del pastel para mostrar esta caja."}
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}

/* ───────── Estilos ───────── */
const styles: Record<string, React.CSSProperties> = {
  page: {
    display: "flex",
    minHeight: "100vh",
    background: "linear-gradient(135deg, #20147cff 0%, #40158aff 100%)",
    padding: 16,
    boxSizing: "border-box",
    gap: 16,
  },
  left: {
    flex: 1,
    display: "grid",
    gridTemplateRows: "1fr 1fr",
    gap: 16,
  },
  topLeft: {
    background: "rgba(255,255,255,0.9)",
    borderRadius: 16,
    boxShadow: "0 6px 16px rgba(0,0,0,0.15)",
    padding: 16,
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
  },
  bottomLeft: {
    background: "rgba(255,255,255,0.9)",
    borderRadius: 16,
    boxShadow: "0 6px 16px rgba(0,0,0,0.15)",
    padding: 16,
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
  },
  title: {
    margin: 0,
    marginBottom: 8,
    fontSize: 18,
    fontWeight: 700,
    color: "#111827",
  },
  hint: {
    marginTop: 6,
    fontSize: 12,
    color: "#374151",
    textAlign: "center",
  },
  right: {
    flex: 1,
    background: "rgba(255,255,255,0.1)",
    borderRadius: 16,
    backdropFilter: "blur(8px)",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    padding: 16,
  },
  boxesWrap: {
    width: "100%",
    maxWidth: 520,
    display: "grid",
    gap: 12,
  },
  textBox: {
    background: "rgba(255,255,255,0.9)",
    borderRadius: 16,
    boxShadow: "0 6px 16px rgba(0,0,0,0.15)",
    padding: 14,
    transition: "opacity 180ms ease, transform 180ms ease",
    cursor: "pointer",
  },
  textBoxTitle: {
    fontSize: 14,
    fontWeight: 700,
    color: "#111827",
    marginBottom: 6,
  },
  textBoxBody: {
    fontSize: 14,
    color: "#1f2937",
  },
};
