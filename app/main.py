from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.auth import router as auth_router
from app.api.v1.users import router as users_router

app = FastAPI(
    title="Auth Service",
    version="1.0.0",
    description="Servicio de autenticación con JWT y Redis",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción especifica los dominios permitidos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/api/v1")
app.include_router(users_router, prefix="/api/v1")


@app.get("/health")
async def health():
    return {"status": "ok"}