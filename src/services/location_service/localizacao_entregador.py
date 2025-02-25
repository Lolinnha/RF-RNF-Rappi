from fastapi import APIRouter
from pydantic import BaseModel
from firebase_admin import db

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
