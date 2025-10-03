import { useState, useEffect } from 'react';
import { Send, Loader2 } from 'lucide-react';
import { useWebSocket } from '../utils/useWebSocket'; // 👈 1. Importar el hook

export default function SimpleAIChat() {
  const [prompt, setPrompt] = useState('');
  const [response, setResponse] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  // 👈 2. Inicializar el hook de WebSocket
  // Asegúrate de que la URL apunte a tu servidor backend
  const endpoint = 'ws://localhost:8000/llm_response';
  const { lastMessage, sendMessage, readyState } = useWebSocket(endpoint);

  // 👈 3. Usar useEffect para manejar los mensajes entrantes
  useEffect(() => {
    if (lastMessage !== null) {
      // Cuando llega el primer mensaje, quitamos el loader
      if (isLoading) {
        setIsLoading(false);
      }
      // Concatenamos la respuesta para simular un stream de texto
      setResponse((prev) => prev + lastMessage.data);
    }
  }, [lastMessage]); // Se ejecuta cada vez que llega un mensaje nuevo

  const handleSubmit = () => {
    // No permitir enviar si no hay texto o la conexión no está abierta
    if (!prompt.trim() || readyState !== WebSocket.OPEN) return;

    // 👈 4. Modificar la lógica de envío
    setIsLoading(true);
    setResponse(''); // Limpiamos la respuesta anterior
    sendMessage(prompt); // Enviamos el prompt a través del WebSocket
    setPrompt(''); // Limpiamos el input
  };

  const handleKeyPress = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };
  
  // Deshabilitar el input y el botón si se está esperando respuesta o si el WebSocket no está conectado
  const isInputDisabled = isLoading || readyState !== WebSocket.OPEN;

  return (
    <div className="flex flex-col h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
      {/* Área de respuesta */}
      <div className="flex-1 overflow-y-auto p-6">
        <div className="max-w-3xl mx-auto">
          {!response && !isLoading && (
            <div className="flex items-center justify-center h-full text-slate-400">
              <div className="text-center">
                <div className="text-6xl mb-4">🤖</div>
                <p className="text-xl">
                  {readyState === WebSocket.OPEN ? 'Escribe tu mensaje para comenzar' : 'Conectando al servidor...'}
                </p>
              </div>
            </div>
          )}

          {isLoading && (
            <div className="flex items-center justify-center py-12">
              <Loader2 className="w-8 h-8 text-purple-400 animate-spin" />
            </div>
          )}

          {response && (
            <div className="bg-slate-800/50 backdrop-blur-sm rounded-2xl p-6 shadow-2xl border border-slate-700">
              <div className="flex items-start gap-3">
                <div className="w-8 h-8 rounded-full bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center flex-shrink-0">
                  <span className="text-white text-sm">AI</span>
                </div>
                <div className="flex-1">
                  <p className="text-slate-100 whitespace-pre-wrap leading-relaxed">
                    {response}
                  </p>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Input del usuario */}
      <div className="border-t border-slate-700 bg-slate-900/50 backdrop-blur-sm p-4">
        <div className="max-w-3xl mx-auto">
          <div className="flex gap-3">
            <input
              type="text"
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Escribe tu mensaje aquí..."
              disabled={isInputDisabled}
              className="flex-1 bg-slate-800 text-slate-100 rounded-xl px-5 py-3 focus:outline-none focus:ring-2 focus:ring-purple-500 placeholder-slate-500 disabled:opacity-50 disabled:cursor-not-allowed"
            />
            <button
              onClick={handleSubmit}
              disabled={isInputDisabled || !prompt.trim()}
              className="bg-gradient-to-r from-purple-600 to-pink-600 text-white rounded-xl px-6 py-3 font-medium hover:from-purple-700 hover:to-pink-700 transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
            >
              {isLoading ? (
                <Loader2 className="w-5 h-5 animate-spin" />
              ) : (
                <>
                  <Send className="w-5 h-5" />
                  <span>Enviar</span>
                </>
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}