from fastapi import FastAPI, Depends, HTTPException
from auth import router as auth_router
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from db import get_db
from models import Incidencia
from deps import get_current_user

app = FastAPI(
    title="Prueba Trimestral 2 - M. Ángeles Domínguez",
    version="1.0.0"
)

app.include_router(auth_router)

class IncidenciaCreate(BaseModel):
    titulo: str = Field(min_length=1, max_length=150)
    descripcion: str = Field(min_length=1)
    prioridad: str = Field(min_length=1, max_length=20)
    estado: str = Field(min_length=1, max_length=20)

class IncidenciaResponse(IncidenciaCreate):
    id: int
    titulo: str
    descripcion: str
    prioridad: str
    estado: str
    class Config:
        from_attributes = True

@app.get("/")
def root():
    return {"ok": True, "mensaje": "API con MySQL lista. Ve a /docs"}

@app.get("/privado")
def privado(usuario: str = Depends(get_current_user)):
    return {"mensaje": f"Hola {usuario}, estás autenticado"}

@app.get("/nombre")
def nombre(usuario: str = Depends(get_current_user)):
    return{"usuario": usuario}

@app.get("/incidencias", response_model=list[IncidenciaResponse])
def listar_incidencias(db: Session = Depends(get_db)):
    try:
        incidencias = db.query(Incidencia).all()
        return incidencias
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/incidencias/{incidencia_id}", response_model=IncidenciaResponse)
def obtener_incidencia(incidencia_id: int, db: Session = Depends(get_db)):
    incidencia = db.query(Incidencia).filter(Incidencia.id == incidencia_id).first()
    if not incidencia:
        raise HTTPException(status_code=404, detail="Incidencia no encontrada")
    return incidencia

@app.post("/incidencias", response_model=IncidenciaResponse, status_code=201)
def crear_incidencia(
    incidencia: IncidenciaCreate,
    db: Session = Depends(get_db),
    usuario: str = Depends(get_current_user)
):
    nueva = Incidencia(
        titulo=incidencia.titulo,
        descripcion=incidencia.descripcion,
        prioridad=incidencia.prioridad,
        estado=incidencia.estado
    )
    db.add(nueva)
    db.commit()
    db.refresh(nueva)
    return nueva