from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import firebase_admin
from firebase_admin import credentials, db

# Inicializando Firebase
cred = credentials.Certificate("path/to/firebase_credentials.json")
firebase_admin.initialize_app(cred, {"databaseURL": "https://your-database.firebaseio.com"})

router = APIRouter()

class LocationUpdate(BaseModel):
    entregador_id: str
    latitude: float
    longitude: float

@router.post("/localizacao")
async def atualizar_localizacao(data: LocationUpdate):
    ref = db.reference(f"entregadores/{data.entregador_id}/localizacao")
    ref.set({"latitude": data.latitude, "longitude": data.longitude})
    return {"message": "Localização atualizada"}
