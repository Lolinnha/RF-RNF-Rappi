from fastapi import APIRouter
from typing import List
import firebase_admin
from firebase_admin import db
import geopy.distance
import time

router = APIRouter()

# Função para calcular entregadores dentro de um raio específico
def buscar_entregadores_por_raio(ponto_central, raio_metros) -> List[str]:
    ref = db.reference("entregadores")
    entregadores = ref.get()
    entregadores_filtrados = []

    print(entregadores)
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

@router.get("/selecionar_entregadores")
async def selecionar_entregadores(latitude: float, longitude: float):
    ponto_central = {"latitude": latitude, "longitude": longitude}
    melhores = calcular_melhores_entregadores(ponto_central)
    
    if not melhores:
        return {"message": "Nenhum entregador encontrado dentro do raio máximo"}
    
    return {"melhores_entregadores": melhores}
