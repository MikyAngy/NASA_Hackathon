from fastapi import FastAPI, HTTPException, WebSocket, Depends
from pydantic import BaseModel
from models import langchain_llm as llm
app = FastAPI()

class requestLlmResponse(BaseModel):
    prompt: str
    
@app.websocket("/llm_response")
async def llm_response(websocket: WebSocket):
    await websocket.accept()
    while True:
        prompt = await websocket.receive_text()
        for token in llm.generate_stream(llm.get_prompt_template(prompt)):
            await websocket.send_text(token)    