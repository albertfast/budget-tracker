from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="SmartBudget API", version="0.1.0")

@app.get("/health")
def health():
    return {"status": "ok"}

class LoginIn(BaseModel):
    email: str
    password: str

@app.post("/auth/login")
def login(payload: LoginIn):
    # Stub only: returns a fake token for now
    return {"access_token": "demo-token", "token_type": "bearer", "email": payload.email}
