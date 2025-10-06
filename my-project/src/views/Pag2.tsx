// src/views/Pag2.tsx  (o el nombre que uses para esta vista)
import * as React from "react";
import { PieChart } from "@mui/x-charts/PieChart";
import { useNavigate } from "react-router-dom"; // 👈 Importamos el hook

interface ArticleAnalysisParameters {
  littletitle: string;
  count: number;
  category: string;
  summarize: string;
}

export interface ArticleAnalysis {
  [key: string]: ArticleAnalysisParameters;
}

export default function PageWithEditableDonutAndChat() {
  const [values, setValues] = React.useState<ArticleAnalysis>(JSON.parse(localStorage.getItem('relevant_art')!));
  const navigate = useNavigate(); // 👈 inicializamos la navegación
  
  // 1️⃣ Agrupar los valores por categoría
  const grouped = Object.values(values).reduce<Record<string, number>>((acc, { category, count }) => {
    acc[category] = (acc[category] || 0) + count;
    return acc;
  }, {});

  // 2️⃣ Crear los datos para la gráfica
  const colorPalette = [
    "#2563EB",
    "#10B981",
    "#F59E0B",
    "#EF4444",
    "#06B6D4",
    "#A855F7",
    "#84CC16",
    "#F97316",
  ];

  const data = Object.entries(grouped).map(([category, total], i) => ({
    label: category,
    value: total,
    color: colorPalette[i % colorPalette.length],
  }));
  React.useEffect(() => {
      // 1. Obtener el STRING desde localStorage
    const jsonString = localStorage.getItem('relevant_art');

    // IMPORTANTE: Verificar que el dato exista antes de continuar
    if (jsonString) {
      try {
        // 2. Convertir el STRING a un OBJETO JavaScript
        const dataObject = JSON.parse(jsonString);

        // // 3. ¡Ahora sí! Aplicar Object.values() al OBJETO
        // const new_values:Articles[] = Object.values(dataObject);
        
        // console.log('Valores obtenidos:', new_values); // Debería ser ['Ana', 30] o similar
        setValues(dataObject);

      } catch (error) {
        console.error("Error al parsear el JSON de localStorage:", error);
      }
    }
    }, []); // Se ejecuta cada vez que llega un mensaje nuevo
  

  // const handleChange = (idx: number, next: number) => {
  //   if (Number.isNaN(next)) return;
  //   const nv = Math.max(0, Math.min(100, next)); // 0–100
  //   setValues((prev) => prev.map((v, i) => (i === idx ? nv : v)));
  // };

  return (
    <div style={styles.page}>
      {/* Izquierda: Gráfica */}
      <div style={styles.left}>
        <div style={styles.chartWrap}>
          <h3 style={styles.title}>Distribución por categorías</h3>

          <div style={styles.chartContainer}>
            <PieChart
              series={[
                {
                  innerRadius: 80,
                  outerRadius: 160,
                  data,
                  arcLabel: (item) => String(item.label),
                  arcLabelMinAngle: 10,
                  paddingAngle: 2,
                },
              ]}
              width={460}
              height={460}
              sx={{ "& .MuiChartsLegend-root": { display: "none" } }}
            />

            {/* 🔽 Botón central que redirige a /pag3 */}
            <button
              style={styles.centerButton}
              onClick={() => navigate("/pag3")}
            >
              Lista
            </button>
          </div>
        </div>
      </div>

      {/* Derecha: Caja de chat (UI) */}
      <div style={styles.right}>
        <div style={styles.chatBox}>
          <div style={styles.chatHeader}>Chat IA (próximamente)</div>
          <div style={styles.chatBody}>
            <div style={styles.msgBot}>
              Hola 👋, aquí podrás hacer preguntas sobre tus gráficos y datos.
            </div>
          </div>
          <div style={styles.chatInputRow}>
            <input
              style={styles.chatInput}
              placeholder="Escribe un mensaje..."
            />
            <button style={styles.chatBtn}>Enviar</button>
          </div>
          <div style={styles.chatHint}>*Aún no tenemos back.</div>
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
  },
  left: {
    flex: 1,
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    padding: 24,
  },
  right: {
    flex: 1,
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    padding: 24,
    background: "rgba(255,255,255,0.08)",
    backdropFilter: "blur(8px)",
  },

  chartWrap: {
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
    gap: 12,
    position: "relative",
  },
  title: {
    margin: 0,
    fontSize: 18,
    fontWeight: 700,
    color: "#FFFFFF",
  },

  chartContainer: {
    position: "relative",
    width: 460,
    height: 460,
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
  },

  centerButton: {
    position: "absolute",
    width: 100,
    height: 100,
    borderRadius: "50%",
    border: "2px solid #FFFFFF",
    background: "#111827",
    color: "#FFFFFF",
    fontWeight: 600,
    cursor: "pointer",
    fontSize: 16,
    transition: "all 0.2s ease",
  },

  chatBox: {
    width: "100%",
    maxWidth: 520,
    background: "rgba(255,255,255,0.9)",
    borderRadius: 16,
    boxShadow: "0 6px 16px rgba(0,0,0,0.15)",
    display: "flex",
    flexDirection: "column",
    overflow: "hidden",
  },
  chatHeader: {
    padding: "12px 14px",
    borderBottom: "1px solid #e5e7eb",
    fontWeight: 700,
    color: "#111827",
  },
  chatBody: {
    padding: 14,
    height: 260,
    overflowY: "auto",
    background: "#ffffff",
  },
  msgBot: {
    maxWidth: "80%",
    background: "#F3F4F6",
    color: "#111827",
    padding: "10px 12px",
    borderRadius: 12,
    fontSize: 14,
  },
  chatInputRow: {
    display: "flex",
    gap: 8,
    padding: 12,
    borderTop: "1px solid #e5e7eb",
    background: "#fff",
  },
  chatInput: {
    flex: 1,
    borderRadius: 10,
    border: "1px solid #e5e7eb",
    padding: "10px 12px",
    outline: "none",
    fontSize: 14,
  },
  chatBtn: {
    borderRadius: 10,
    border: "none",
    background: "#111827",
    color: "#fff",
    padding: "10px 14px",
    fontWeight: 600,
    cursor: "pointer",
  },
  chatHint: {
    padding: "6px 12px 12px",
    fontSize: 12,
    color: "#6B7280",
  },
};
