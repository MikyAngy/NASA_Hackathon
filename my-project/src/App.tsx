// src/App.tsx
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import SimpleAIChat from "./views/chat";
import Pag1 from "./views/Pag1";
import Pag2 from "./views/Pag2";
import Pag3 from "./views/Pag3";
import Pag4 from "./views/Pag4";
import Pag5 from "./views/Pag5";

function App() {
  return (
    <Router>
      <Routes>
        {/* Página de inicio */}
        <Route path="/" element={<Pag1 />} />

        {/* Otras páginas */}
        <Route path="/pag2" element={<Pag2 />} />
        <Route path="/pag3" element={<Pag3 />} />
        <Route path="/pag4" element={<Pag4 />} />
        <Route path="/pag5" element={<Pag5 />} />

        {/* Fallback si no hay ruta */}
        <Route path="*" element={<Pag1 />} />
      </Routes>
    </Router>
  );
}

export default App;
