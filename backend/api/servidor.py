from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .contratos import router as contratos_router
from .cierres import router as cierres_router
from .dashboard import router as dashboard_router

app = FastAPI(title="API de Gestión de Contratos Internacionales")

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especificar los orígenes permitidos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers
app.include_router(contratos_router)
app.include_router(cierres_router)
app.include_router(dashboard_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 