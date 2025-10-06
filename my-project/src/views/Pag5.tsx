// src/pages/PageDocAndChat.tsx
import * as React from "react";
import { useSearchParams } from "react-router-dom";
import { useWebSocket } from "../utils/useWebSocket";
import pdfImage from './pdf_Art.png';

  const CHART_HEIGHT = 380;


// 🧱 Interfaz para la estructura más interna y repetida
interface AnalisisItem {
  porcentaje: number;
  justificacion: string;
}

// 🏗️ Interfaz para el objeto que contiene los diferentes análisis
interface AnalisisCuantitativo {
  progreso_cientifico: AnalisisItem;
  lagunas_de_conocimiento: AnalisisItem;
  consenso_y_desacuerdo: AnalisisItem;
}

// 🏢 Interfaz principal que representa la estructura completa del JSON
export interface DatosAnalisis {
  analisis_cuantitativo: AnalisisCuantitativo;
}


export default function PageDocAndChat() {
  const DOC_URL = "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC4136787/";
  const [datos, setDatos] = React.useState<DatosAnalisis>();
  const [searchParams] = useSearchParams();
    const [response, setResponse] = React.useState('');
  


  // 2. Usa el método .get('nombreDeLaClave') para obtener el valor.
  const title = searchParams.get('title');
  
  React.useEffect(() => {
  // 1. Define una función async DENTRO de useEffect
  const fetchAndRedirect = async () => {
    try {
      // 2. Realiza la petición fetch
      const response = await fetch('http://localhost:8000/analyze_article', {
        method: 'POST', // Especifica el método
        headers: {
          'Content-Type': 'application/json', // Informa al servidor que envías JSON
        },
        body: JSON.stringify({'title':title}), // Convierte el objeto de JS a un string JSON
      });

      if (!response.ok) {
        // Si el servidor responde con un error (ej: 404, 500)
        throw new Error(`Error HTTP: ${response.status}`);
      }

      // 3. Procesa la respuesta del servidor
      const result = await response.json();

      console.log(result)
      setDatos(result)

    } catch (err: any) {
      // setError(err.message);
      console.error('Error al enviar los datos:', err);
    }
  };

  // 2. Llama a la función inmediatamente
  // fetchAndRedirect();

}, []);

 const endpoint = 'ws://localhost:8000/llm_response';
  const { lastMessage, sendMessage, readyState } = useWebSocket(endpoint);

  // 👈 3. Usar useEffect para manejar los mensajes entrantes
  React.useEffect(() => {
    if (lastMessage !== null) {
      // Concatenamos la respuesta para simular un stream de texto
      setResponse((prev) => prev + lastMessage.data);
    }
  }, [lastMessage]); // Se ejecuta cada vez que llega un mensaje nuevo

  // // Chat state (UI only; sin backend)
  // type Msg = { role: "user" | "ai"; text: string };
  // const [messages, setMessages] = React.useState<Msg[]>([
  //   { role: "ai", text: "¡Hola! Pregúntame algo sobre el artículo de la izquierda." },
  // ]);
  const [input, setInput] = React.useState("");

  const send = () => {
    // No permitir enviar si no hay texto o la conexión no está abierta
    if (!input.trim() || readyState !== WebSocket.OPEN) return;

    // 👈 4. Modificar la lógica de envío
    sendMessage(input); // Enviamos el prompt a través del WebSocket
    setInput('')
  };

  const onKeyDown: React.KeyboardEventHandler<HTMLInputElement> = (e) => {
    if (e.key === "Enter") send();
  };

  // const categories = Object.entries(items).map((_,i) => i+1);
  // const values = Object.entries(items).map(([k,v]) => v);

  const categories = ['progreso_cientifico','lagunas_de_conocimiento','consenso_y_desacuerdo'];
  const values = [datos?.analisis_cuantitativo.progreso_cientifico.porcentaje ?? null,datos?.analisis_cuantitativo.lagunas_de_conocimiento.porcentaje ?? null,datos?.analisis_cuantitativo.consenso_y_desacuerdo.porcentaje ?? null];

  return (
    <div style={styles.page}>
      {/* Izquierda: página externa embebida */}
      <div style={styles.left}>
        {/* <img src={pdfImage} alt="" style={styles.image}/> */}
        <div style={styles.leftHeader}></div>
        {/* <BarChart
          xAxis={[{ data: categories, scaleType: "band" }]}
          series={[{ data: values, color: "#2563EB" }]}
          height={CHART_HEIGHT}
          // Oculta la leyenda si aparece:
          sx={{ "& .MuiChartsLegend-root": { display: "none" } }}
        /> */}
        <div style={styles.leftHeader}>
          <h3 style={styles.title}>Artículo (NCBI / PMC)</h3>
          <a style={styles.openBtn} href={DOC_URL} target="_blank" rel="noreferrer">
            Abrir en pestaña nueva
          </a>
        </div>
        <div style={styles.iframeWrap}>
          {/* Nota: si el sitio bloquea iframes, usa el botón "Abrir en pestaña nueva" 
          <iframe
            src={DOC_URL}
            style={styles.iframe}
            title="NCBI Article"
            referrerPolicy="no-referrer"
            sandbox="allow-scripts allow-same-origin allow-popups allow-forms"
          />*/}
        </div>
      </div>

      {/* Derecha: Chat IA */}
      <div style={styles.right}>
        <div style={styles.chatBox}>
          <div style={styles.chatHeader}>Chat IA sobre el artículo</div>
          <div style={styles.chatBody}>
            {response} <br />
          </div>
          <div style={styles.chatInputRow}>
            <input
              style={styles.chatInput}
              placeholder="Escribe tu pregunta…"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={onKeyDown}
            />
            <button style={styles.chatBtn} onClick={send}>
              Enviar
            </button>
          </div>
          <div style={styles.chatHint}>
            *Aún sin backend: conecta tu endpoint (por ejemplo <code>/api/chat</code>) para responder con base en
            la página de la izquierda.
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
    padding: 16,
    gap: 16,
    boxSizing: "border-box",
  },
  left: {
    flex: 1,
    display: "flex",
    flexDirection: "column",
    background: "rgba(255,255,255,0.9)",
    borderRadius: 16,
    boxShadow: "0 6px 16px rgba(0,0,0,0.15)",
    overflow: "hidden",
  },
  image: {
    width: '100%',
    height: '100%',
    objectFit: 'cover', // La magia está aquí
    // objectPosition: 'center' // Opcional: centra la imagen
  },
  leftHeader: {
    display: "flex",
    alignItems: "center",
    justifyContent: "space-between",
    padding: "10px 12px",
    borderBottom: "1px solid #e5e7eb",
    background: "#fff",
  },
  title: { margin: 0, fontSize: 16, fontWeight: 700, color: "#111827" },
  openBtn: {
    background: "#111827",
    color: "#fff",
    padding: "8px 12px",
    borderRadius: 10,
    textDecoration: "none",
    fontWeight: 600,
  },
  iframeWrap: { flex: 1, position: "relative" },
  iframe: {
    border: "none",
    width: "100%",
    height: "100%",
    background: "#fff",
  },

  right: {
    flex: 1,
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    padding: 0,
    background: "rgba(255,255,255,0.1)",
    borderRadius: 16,
    backdropFilter: "blur(8px)",
  },
  chatBox: {
    width: "100%",
    maxWidth: 540,
    background: "rgba(255,255,255,0.95)",
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
    background: "#fff",
  },
  chatBody: {
    padding: 14,
    height: 420,
    overflowY: "auto",
    background: "#ffffff",
    display: "flex",
    flexDirection: "column",
    gap: 8,
  },
  msg: {
    maxWidth: "85%",
    padding: "10px 12px",
    borderRadius: 12,
    fontSize: 14,
    lineHeight: 1.4,
  },
  msgAI: { background: "#F3F4F6", color: "#111827", alignSelf: "flex-start" },
  msgUser: {
    background: "#111827",
    color: "#fff",
    alignSelf: "flex-end",
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
    padding: "0 12px 12px",
    fontSize: 12,
    color: "#6B7280",
  },
};
