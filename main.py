from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from typing import List
import json

app = FastAPI()

# ==========================================
# 1. GESTOR DE WEBSOCKETS (O Túnel)
# ==========================================
class ConnectionManager:
    def __init__(self):
        # Guarda todos os operadores que estão com o site aberto
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        # Envia a mensagem para todos os ecrãs do Syncro ligados
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()

# ==========================================
# 2. ROTAS DO WEBHOOK DA META
# ==========================================
@app.get("/webhook")
async def verify_webhook(request: Request):
    # A senha que configurou no painel da Meta
    VERIFY_TOKEN = "meu_codigo_secreto_123" 
    
    mode = request.query_params.get("hub.mode")
    token = request.query_params.get("hub.verify_token")
    challenge = request.query_params.get("hub.challenge")
    
    if mode == "subscribe" and token == VERIFY_TOKEN:
        return int(challenge)
    return {"error": "Token de verificação inválido"}

@app.post("/webhook")
async def receive_whatsapp_message(request: Request):
    # Recebe os dados enviados pela Meta
    data = await request.json()
    
    try:
        # Extrai a mensagem de texto e o número do cliente (estrutura padrão da Meta)
        entry = data["entry"][0]
        changes = entry["changes"][0]
        value = changes["value"]
        
        if "messages" in value:
            mensagem_info = value["messages"][0]
            contato_info = value["contacts"][0]
            
            # Monta um pacote simples para enviar ao Frontend
            pacote_para_frontend = {
                "tipo": "mensagem_recebida",
                "nome_cliente": contato_info.get("profile", {}).get("name", "Cliente"),
                "numero_cliente": mensagem_info.get("from"),
                "texto": mensagem_info.get("text", {}).get("body", "")
            }
            
            # Dispara a mensagem pelo túnel WebSocket em tempo real!
            await manager.broadcast(json.dumps(pacote_para_frontend))
            
    except Exception as e:
        print(f"Erro ao processar mensagem: {e}")
        
    return {"status": "ok"}

# ==========================================
# 3. ROTA DO WEBSOCKET PARA O FRONTEND
# ==========================================
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    # Quando o site Syncro se liga, aceitamos a ligação
    await manager.connect(websocket)
    try:
        while True:
            # Mantém o túnel aberto (no futuro, receberemos as mensagens enviadas pelo operador aqui)
            data = await websocket.receive_text()
            print(f"Operador enviou: {data}")
    except WebSocketDisconnect:
        # Se o operador fechar o separador do navegador, desligamos a ligação
        manager.disconnect(websocket)
