from fastapi import APIRouter, HTTPException
import firebase_admin
from firebase_admin import db
from services

router = APIRouter()

@router.post("/atribuir_pedido")
async def atribuir_pedido(pedido_id: str, latitude: float, longitude: float):
    ponto_central = {"latitude": latitude, "longitude": longitude}
    melhores_entregadores = calcular_melhores_entregadores(ponto_central)

    if not melhores_entregadores:
        raise HTTPException(status_code=404, detail="Nenhum entregador disponível dentro do raio máximo")

    ref = db.reference(f"pedidos/{pedido_id}/candidatos")
    ref.set(melhores_entregadores)

    # Simula notificação (substituir por push real)
    return {"message": "Pedido enviado aos entregadores", "candidatos": melhores_entregadores}
