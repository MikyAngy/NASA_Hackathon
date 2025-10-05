// src/views/Pag1.tsx  (o CenterSearchWeb.tsx)
import React, { useState } from "react";
import { useNavigate } from "react-router-dom"; // 👈 Importamos el hook
import portada from "../assets/nasaportada.png"; // tu imagen de fondo

export default function CenterSearchWeb() {
  const [q, setQ] = useState("");
  const navigate = useNavigate(); // 👈 inicializamos el navegador

  const onSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    console.log("Buscar:", q);

    // 👇 redirige a la página 2
    navigate("/pag2");
  };

  return (
    <div style={styles.container(portada)}>
      {/* Buscador principal */}
      <h1 style={styles.title}>Explorer One Search</h1>
      <form onSubmit={onSubmit} style={styles.form}>
        <input
          style={styles.input}
          placeholder="Buscar…"
          value={q}
          onChange={(e) => setQ(e.target.value)}
        />
        <button style={styles.btn} type="submit">
          Buscar
        </button>
      </form>

      {/* Cuadros de texto flotantes */}
      <div style={styles.boxBottomLeft}>
        <p style={styles.boxText}>
          🌍 Explora miles de artículos científicos y bases de datos en tiempo real.
        </p>
      </div>

      <div style={styles.boxBottomRight}>
        <p style={styles.boxText}>
          🚀 Con tecnología de búsqueda inteligente y asistencia por IA.
        </p>
      </div>

      <div style={styles.boxTopRight}>
        <p style={styles.boxText}>
          🛰️ NASA Hackathon 2025 · Explorer One Project
        </p>
      </div>
    </div>
  );
}

const styles = {
  container: (bg: string): React.CSSProperties => ({
    minHeight: "100vh",
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
    justifyContent: "center",
    backgroundImage: `url(${bg})`,
    backgroundSize: "cover",
    backgroundPosition: "center",
    backgroundRepeat: "no-repeat",
    backgroundColor: "rgba(0,0,0,0.4)",
    backgroundBlendMode: "overlay",
    padding: 24,
    position: "relative",
    overflow: "hidden",
  }),
  title: {
    margin: 0,
    fontSize: 32,
    fontWeight: 700,
    color: "#FFFFFF",
    textShadow: "0 2px 8px rgba(0,0,0,0.5)",
  },
  form: { display: "flex", gap: 8, width: "100%", maxWidth: 560, marginTop: 16 },
  input: {
    flex: 1,
    padding: "12px 14px",
    borderRadius: 12,
    border: "1px solid rgba(255,255,255,0.4)",
    background: "rgba(255,255,255,0.85)",
    fontSize: 16,
    outline: "none",
  } as React.CSSProperties,
  btn: {
    padding: "12px 16px",
    borderRadius: 12,
    border: "none",
    background: "#111827",
    color: "white",
    fontSize: 14,
    fontWeight: 500,
    cursor: "pointer",
  } as React.CSSProperties,

  boxBottomLeft: {
    position: "absolute",
    bottom: "12%",
    left: "6%",
    background: "rgba(255, 255, 255, 0.3)",
    backdropFilter: "blur(8px)",
    WebkitBackdropFilter: "blur(8px)",
    borderRadius: 16,
    padding: "16px 20px",
    color: "#111827",
    maxWidth: 280,
    boxShadow: "0 4px 10px rgba(0,0,0,0.15)",
  } as React.CSSProperties,

  boxBottomRight: {
    position: "absolute",
    bottom: "12%",
    right: "6%",
    background: "rgba(255,255,255,0.3)",
    backdropFilter: "blur(8px)",
    WebkitBackdropFilter: "blur(8px)",
    borderRadius: 16,
    padding: "16px 20px",
    color: "#111827",
    maxWidth: 280,
    textAlign: "right",
    boxShadow: "0 4px 10px rgba(0,0,0,0.15)",
  } as React.CSSProperties,

  boxTopRight: {
    position: "absolute",
    top: "8%",
    right: "6%",
    background: "rgba(255,255,255,0.3)",
    backdropFilter: "blur(8px)",
    WebkitBackdropFilter: "blur(8px)",
    borderRadius: 16,
    padding: "16px 20px",
    color: "#111827",
    maxWidth: 280,
    textAlign: "right",
    boxShadow: "0 4px 10px rgba(0,0,0,0.15)",
  } as React.CSSProperties,

  boxText: {
    margin: 0,
    fontSize: 14,
    fontWeight: 500,
    lineHeight: 1.4,
  } as React.CSSProperties,
};
