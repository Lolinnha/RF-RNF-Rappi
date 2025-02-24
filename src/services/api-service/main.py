from fastapi import FastAPI, APIRouter, HTTPException
from pydantic import BaseModel
import firebase_admin
from firebase_admin import credentials, db
import geopy.distance
import time
from typing import List

# Inicializando o Firebase
cred = credentials.Certificate("path/to/firebase_credentials.json")
firebase_admin.initialize_app(cred, {"databaseURL": "https://your-database.firebaseio.com"})

app = FastAPI()

# Criando o router para os endpoints
router = APIRouter()

# Modelo para atualização de localização
class LocationUpdate(BaseModel):
    entregador_id: str
    latitude: float
    longitude: float

# Função para calcular entregadores dentro de um raio específico
def buscar_entregadores_por_raio(ponto_central, raio_metros) -> List[str]:
    ref = db.reference("entregadores")
    entregadores = ref.get()
    entregadores_filtrados = []

    for id, dados in entregadores.items():
        if not dados.get("disponivel") or dados.get("saldo", 0) <= 0:
            continue
        
        localizacao = dados.get("localizacao")
        if not localizacao:
            continue
        
        distancia = geopy.distance.geodesic(
            (ponto_central["latitude"], ponto_central["longitude"]),
            (localizacao["latitude"], localizacao["longitude"])
        ).meters

        if distancia <= raio_metros:
            entregadores_filtrados.append((id, dados))

    return entregadores_filtrados

# Função que expande a busca a cada minuto
def calcular_melhores_entregadores(ponto_central):
    raio_metros = 500  # Raio inicial
    max_tentativas = 6  # Máximo de 6 tentativas (~6 min)
    
    for _ in range(max_tentativas):
        entregadores = buscar_entregadores_por_raio(ponto_central, raio_metros)
        
        if entregadores:
            top_3 = sorted(entregadores, key=lambda x: x[1]["saldo"], reverse=True)[:3]
            return [id for id, _ in top_3]
        
        raio_metros += 500  # Aumenta o raio de busca em 500m
        time.sleep(60)  # Aguarda 1 minuto antes de expandir a busca

    return []

# Endpoint para atualizar a localização do entregador
@router.post("/localizacao")
async def atualizar_localizacao(data: LocationUpdate):
    ref = db.reference(f"entregadores/{data.entregador_id}/localizacao")
    ref.set({"latitude": data.latitude, "longitude": data.longitude})
    return {"message": "Localização atualizada"}

# Endpoint para atribuir pedido a entregadores
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

# Endpoint para selecionar melhores entregadores com base na localização
@router.get("/selecionar_entregadores")
async def selecionar_entregadores(latitude: float, longitude: float):
    ponto_central = {"latitude": latitude, "longitude": longitude}
    melhores = calcular_melhores_entregadores(ponto_central)
    
    if not melhores:
        return {"message": "Nenhum entregador encontrado dentro do raio máximo"}
    
    return {"melhores_entregadores": melhores}

# Endpoint para responder pedido por entregador
@router.post("/responder_pedido")
async def responder_pedido(pedido_id: str, entregador_id: str):
    ref = db.reference(f"pedidos/{pedido_id}/candidatos")
    candidatos = ref.get()

    if not candidatos or entregador_id not in candidatos:
        raise HTTPException(status_code=400, detail="Entregador não está na lista de candidatos")

    ref_final = db.reference(f"pedidos/{pedido_id}/entregador_atribuido")
    ref_final.set(entregador_id)

    return {"message": "Pedido aceito pelo entregador", "entregador": entregador_id}

# Adicionando o router à aplicação FastAPI
app.include_router(router)
