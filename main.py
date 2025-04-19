from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from Config.db import engine
from Dominio.Modelos.Base import Base
from Presentacion.API.Rutas import ListaDoble_Rutas, Vuelo_Rutas

# Crear las tablas en la base de datos
Base.metadata.create_all(bind=engine)

# Crear la aplicación FastAPI
app = FastAPI(
    title="API del Aeropuerto",
    description="API para gestionar vuelos utilizando una lista doblemente enlazada",
    version="1.0.0"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permitir todos los orígenes
    allow_credentials=True,
    allow_methods=["*"],  # Permitir todos los métodos
    allow_headers=["*"],  # Permitir todos los headers
)

# Incluir rutas
app.include_router(Vuelo_Rutas.router)
app.include_router(ListaDoble_Rutas.router)

@app.get("/")
def read_root():
    return {"message": "Bienvenido a la API del Aeropuerto!"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
