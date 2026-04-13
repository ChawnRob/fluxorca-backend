from fastapi import FastAPI
from pydantic import BaseModel
import json
import os
from datetime import datetime

app = FastAPI()

MEMORY_FILE = "memory.json"

# ----------- MODELS -----------

class ChatRequest(BaseModel):
    user_id: str
    message: str
    model: str = "auto"

# ----------- MEMORY -----------

def load_memory():
    if not os.path.exists(MEMORY_FILE):
        return {}
    with open(MEMORY_FILE, "r") as f:
        return json.load(f)

def save_memory(data):
    with open(MEMORY_FILE, "w") as f:
        json.dump(data, f, indent=2)

def add_memory(user_id, content):
    data = load_memory()
    if user_id not in data:
        data[user_id] = []

    data[user_id].append({
        "content": content,
        "created_at": datetime.utcnow().isoformat()
    })

    save_memory(data)

def get_memory(user_id):
    data = load_memory()
    return data.get(user_id, [])

# ----------- MODEL ROUTER -----------

def choose_model(model, message):
    if model != "auto":
        return model

    # logique simple
    if "analyse" in message or "stratégie" in message:
        return "gpt"
    elif "émotion" in message or "humain" in message:
        return "claude"
    else:
        return "mistral"

def call_model(model, message):
    # MOCK pour l’instant (on branchera API après)
    return f"[{model.upper()}] Réponse à: {message}"

# ----------- ROUTES -----------

@app.get("/")
def root():
    return {"status": "OpenChawn running"}

@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/chat")
def chat(req: ChatRequest):
    user_id = req.user_id
    message = req.message

    memory = get_memory(user_id)
    context = " ".join([m["content"] for m in memory[-5:]])

    full_prompt = f"""
    Tu es un assistant .

    Ta mission:
    Répondre simplement au message de l'utilisateur .
    
    REGLES STRICTES :
    -Tu ne fais AUCUNE analyse
    -Tu ne parle JAMAIS de QEI
    -Tu ne structure Pas
    -Tu ne donne QUE LA  Réponse finale 
    
    Format OBLIGATOIRE :
    Retourne UNIQUEMENT du texte brut.
    Message utilisateur :
    {message}
    """ 
    model = choose_model(req.model, message)
    response = call_model(model, full_prompt)
   
    try:
    parsed = json.loads(response) if isinstance(response, str) else response
    if isinstance(parsed, dict) and "answer" in parsed:
        response = parsed["answer"]
except Exception:
    pass

    add_memory(user_id, message)

   if isinstance(response, dict) and "answer" in response:
        response =  response["answer"]

return response

@app.get("/memory/{user_id}")
def memory(user_id: str):
    return get_memory(user_id)
