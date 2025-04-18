from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from . import coffee_price, proveedores

app = FastAPI(title="API de Gestión de Café")

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers
app.include_router(coffee_price.router, prefix="/api")
app.include_router(proveedores.router, prefix="/api") 