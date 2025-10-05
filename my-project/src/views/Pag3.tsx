// src/views/Pag2.tsx (o donde lo uses)
import * as React from "react";
import { useNavigate } from "react-router-dom";
import { BarChart } from "@mui/x-charts/BarChart";
import type { Articles } from "./Pag2";

type Item = { id: number; label: string; href: string };

export default function PageWithBarsAndChecklist() {
  // 10 elementos seleccionables
  // const items: Item[] = [
  //   { id: 1, label: "Artículo 1", href: "#" },
  //   { id: 2, label: "Artículo 2", href: "#" },
  //   { id: 3, label: "Artículo 3", href: "#" },
  //   { id: 4, label: "Artículo 4", href: "#" },
  //   { id: 5, label: "Artículo 5", href: "#" },
  //   { id: 6, label: "Artículo 6", href: "#" },
  //   { id: 7, label: "Artículo 7", href: "#" },
  //   { id: 8, label: "Artículo 8", href: "#" },
  //   { id: 9, label: "Artículo 9", href: "#" },
  //   { id: 10, label: "Artículo 10", href: "#" },
  // ];

  const [items, ] = React.useState<Articles>(JSON.parse(localStorage.getItem('relevant_art')!));
  

  const [selected, setSelected] = React.useState<Record<number, boolean>>({});
  const navigate = useNavigate();

  const toggle = (id: number) =>
    setSelected((s) => ({ ...s, [id]: !s[id] }));

  const selectedIds = Object.entries(selected)
    .filter(([, v]) => v)
    .map(([k]) => Number(k));
  const count = selectedIds.length;

  // Datos base (1 sola serie, orden mayor→menor)
  const data = [
    { name: "NombreA", value: 8 },
    { name: "NombreB", value: 6 },
    { name: "NombreC", value: 4 },
    { name: "NombreD", value: 3 },
    { name: "NombreE", value: 2 },
  ].sort((a, b) => b.value - a.value);

  const categories = Object.entries(items).map((_,i) => i+1);
  console.log(categories)
  const values = Object.entries(items).map(([k,v]) => v);

  // Acción del botón según cantidad
  const handlePrimaryAction = () => {
    if (count === 1) {
      navigate("/pag5"); // Analizar
    } else if (count >= 2) {
      navigate("/pag4"); // Comparar
    }
  };

  const buttonLabel = count === 1 ? "Analizar" : count >= 2 ? "Comparar" : "";

  // ---- Click en barras -> /pag5 (overlay que calcula el índice por X) ----
  const chartWrapRef = React.useRef<HTMLDivElement | null>(null);
  const CHART_WIDTH = 560;   // el mismo width del contenedor
  const CHART_HEIGHT = 380;

  const onOverlayClick: React.MouseEventHandler<HTMLDivElement> = (e) => {
    if (!chartWrapRef.current) return;
    const rect = chartWrapRef.current.getBoundingClientRect();
    const x = e.clientX - rect.left;

    const n = categories.length;
    if (n <= 0) return;

    // Bandas aproximadas (asumiendo bandas uniformes dentro del ancho)
    const band = CHART_WIDTH / n;
    const idx = Math.floor(x / band);

    if (idx >= 0 && idx < n) {
      // Aquí podrías leer la categoría clicada si lo necesitas:
      // const clickedName = categories[idx];
      navigate("/pag5");
    }
  };

  return (
    <div style={styles.page}>
      {/* Izquierda: checklist */}
      <div style={styles.left}>
        <div style={styles.card}>
          <div style={styles.cardHeader}>
            <h3 style={styles.cardTitle}>Selecciona artículos</h3>

            {/* Botón condicional */}
            {count >= 1 && (
              <button style={styles.primaryBtn} onClick={handlePrimaryAction}>
                {buttonLabel} {count > 0 ? `(${count})` : ""}
              </button>
            )}
          </div>

          <ul style={styles.list}>
            {Object.entries(items).map(([k,v],key) => (
              <li key={key} style={styles.listItem}>
                {/* <label style={styles.checkRow}> */}
                  {/* <input
                    type="checkbox"
                    checked={!!selected[it.id]}
                    onChange={() => toggle(it.id)}
                    style={styles.checkbox}
                  /> */}
                  <div
                    style={{ ...styles.link, cursor: 'pointer' }} // 👈 Se añade cursor: 'pointer'
                    onClick={() => navigate(`/pag5?title=${encodeURIComponent(k)}`)}
                  >
                    {key + 1} {k}
                  </div>
                {/* </label> */}
              </li>
            ))}
          </ul>
        </div>
      </div>

      {/* Derecha: gráfica de barras con overlay clicable */}
      <div style={styles.right}>
        <div style={styles.chartCard}>
          <h3 style={styles.chartTitle}>Artículos de tu interés</h3>

          <div
            ref={chartWrapRef}
            style={{ position: "relative", width: CHART_WIDTH }}
          >
            <BarChart
              xAxis={[{ data: categories, scaleType: "band" }]}
              series={[{ data: values, color: "#2563EB" }]}
              height={CHART_HEIGHT}
              // Oculta la leyenda si aparece:
              sx={{ "& .MuiChartsLegend-root": { display: "none" } }}
            />

            {/* Overlay transparente que detecta el índice por X */}
            <div
              onClick={onOverlayClick}
              style={{
                position: "absolute",
                inset: 0,
                background: "transparent",
                cursor: "pointer",
              }}
              title="Haz click en una barra para ir a la página 5"
            />
          </div>
        </div>
      </div>
    </div>
  );
}

const styles: Record<string, React.CSSProperties> = {
  page: {
    display: "flex",
    minHeight: "100vh",
    background: "linear-gradient(135deg, #20147cff 0%, #40158aff 100%)",
    padding: 24,
    boxSizing: "border-box",
  },
  left: {
    flex: 1,
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    padding: 12,
  },
  right: {
    flex: 1,
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    padding: 12,
  },
  card: {
    width: "100%",
    maxWidth: 520,
    background: "rgba(255,255,255,0.9)",
    borderRadius: 16,
    boxShadow: "0 6px 16px rgba(0,0,0,0.15)",
    padding: 18,
  },
  cardHeader: {
    display: "flex",
    alignItems: "center",
    justifyContent: "space-between",
    gap: 12,
    marginBottom: 10,
  },
  cardTitle: {
    margin: 0,
    fontSize: 18,
    fontWeight: 700,
    color: "#111827",
  },
  primaryBtn: {
    border: "none",
    borderRadius: 12,
    padding: "10px 14px",
    background: "#111827",
    color: "#fff",
    fontWeight: 600,
    cursor: "pointer",
  },
  list: {
    listStyle: "none",
    padding: 0,
    margin: 0,
    display: "grid",
    gridTemplateColumns: "1fr",
    gap: 8,
  },
  listItem: {},
  checkRow: {
    display: "flex",
    alignItems: "center",
    gap: 10,
    cursor: "pointer",
  },
  checkbox: {
    width: 18,
    height: 18,
  },
  link: {
    color: "#1f2937",
    textDecoration: "underline",
  },
  chartCard: {
    width: "100%",
    maxWidth: 720,
    background: "rgba(255,255,255,0.9)",
    borderRadius: 16,
    boxShadow: "0 6px 16px rgba(0,0,0,0.15)",
    padding: 18,
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
  },
  chartTitle: {
    margin: 0,
    marginBottom: 10,
    fontSize: 18,
    fontWeight: 700,
    color: "#111827",
  },
};
