from fastapi import FastAPI
import firebase_admin
from firebase_admin import credentials
from services.accept_order_service.aceitar_pedido import router as pedidos_router
from services.alocation_service.alocacao_entregador import router as alocacao_router
from services.assignment_service.atribuicao_entregador import router as atribuicao_router
from services.location_service.localizacao_entregador import router as localizacao_router

# Inicializando o Firebase
cred = credentials.Certificate("./config/alocacao-entregadores-firebase-credenciais.json")
firebase_admin.initialize_app(cred, {"databaseURL": "https://alocacao-entregadores-default-rtdb.firebaseio.com/"})


# Criando a aplicação FastAPI
app = FastAPI()

# Incluindo os routers de cada serviço
app.include_router(pedidos_router)
app.include_router(alocacao_router)
app.include_router(atribuicao_router)
app.include_router(localizacao_router)

