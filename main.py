from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import PlainTextResponse
import uvicorn

app = FastAPI()

# Esta é a sua senha de validação. Usaremos ela na configuração da Meta.
VERIFY_TOKEN = "EAAYh4JuwVGoBSjneyhZBdAzBirV7oyzYRtWnZCOK6SA1MJTwUvVQjhVSOrlXZBnzyjdk3cjQELrNZCtAAiP5u2OlxhLxPChVogfqcpsBgrvmqudQjf6Ugk2j2f11a0OJTIaJ47ZCA1wr5uZCTevUJ9Q0RiILaOPoaewNW4QdcG4yOegG83IfOFOKI6enGNiQyOZCPg7XAo7ICa4s5ErePnpIDkn9E1ZBccDala2Pa97CemICgvBP5xR3SgZB4R8VIejchZBb67hscBOM6wjAUCtYTF"

@app.get("/webhook")
async def verify_webhook(request: Request):
    """Rota usada pela Meta apenas uma vez para validar seu servidor."""
    mode = request.query_params.get("hub.mode")
    token = request.query_params.get("hub.verify_token")
    challenge = request.query_params.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        print("Webhook verificado com sucesso pela Meta!")
        return PlainTextResponse(content=challenge, status_code=200)
    
    raise HTTPException(status_code=403, detail="Token inválido")

@app.post("/webhook")
async def receive_message(request: Request):
    """Rota usada pela Meta para enviar as mensagens recebidas."""
    body = await request.json()
    print("Nova mensagem recebida do WhatsApp:")
    print(body)
    return {"status": "ok"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)