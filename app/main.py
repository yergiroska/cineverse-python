from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.routers import auth, favorites

# Crear instancia de FastAPI
app = FastAPI(
    title="CineVerse API",
    description="API para plataforma de seguimiento de películas y series",
    version="1.0.0",
    docs_url="/api/docs",  # Swagger UI
    redoc_url="/api/redoc"  # ReDoc
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Ruta de prueba
@app.get("/")
async def root():
    """Endpoint raíz de bienvenida"""
    return {
        "message": "Bienvenido a CineVerse API",
        "version": "1.0.0",
        "docs": "/api/docs"
    }


@app.get("/health")
async def health_check():
    """Health check para verificar que la API está funcionando"""
    return {
        "status": "healthy",
        "environment": settings.ENVIRONMENT
    }


# Registrar routers
app.include_router(auth.router, prefix="/api", tags=["Authentication"])
app.include_router(favorites.router, prefix="/api/favorites", tags=["Favorites"])