from fastapi import FastAPI, Depends, HTTPException, status, Query
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy.sql import text
from .database import get_db
from passlib.context import CryptContext

from . import models, schemas, crud, auth
from .database import get_db

app = FastAPI()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Define el esquema de seguridad OAuth2
# El argumento tokenUrl es la URL de tu endpoint de login
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Función que obtendrá el usuario actual del token
def get_current_user(
    db: Session = Depends(get_db), 
    token: str = Depends(oauth2_scheme)
):
    user = crud.get_user_by_token(db, token)
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or inactive authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user

# Endpoint para verificar la conexión a la base de datos
@app.get("/health")
def check_db_connection(db: Session = Depends(get_db)):
    """
    Permite hacer check de salud de la API y conexión a la DB.
    """
    try:
        # Ahora usa text() para envolver la consulta SQL
        data = db.execute(text("select 1"))
        return {"status": "ok", "message": "Successfully connected to the database."}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database connection failed: {e}"
        )

# Endpoint para registrar un nuevo usuario
@app.post("/register", response_model=schemas.User)
def register_user(
    user: schemas.UserCreate, 
    db: Session = Depends(get_db)
    ):
    """
    Permite hacer registro.
    """
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = pwd_context.hash(user.password)
    new_user = crud.create_user(db=db, user=user, hashed_password=hashed_password)
    return new_user

# Endpoint para login
@app.post("/token")
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    Permite hacer login.
    """
    user = crud.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = auth.create_access_token(data={"sub": user.email})
    
    return {"access_token": access_token, "token_type": "bearer"}

# Endpoint 
@app.get("/leads", response_model=schemas.PaginatedLeads)
def read_leads(
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100)
):
    """
    Obtiene una lista paginada de todos los leads.
    """
    total_leads = crud.get_leads_count(db)
    leads = crud.get_leads(db, skip=skip, limit=limit)
    return schemas.PaginatedLeads(total=total_leads, leads=leads)

@app.get("/leads/{lead_id}", response_model=schemas.Lead)
def read_lead_by_id(
    lead_id: str, 
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user), # dependencia para proteger el endpoint
    ):
    """
    Obtiene un lead específico por su ID.
    """
    lead = crud.get_lead_by_id(db, lead_id=lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    return lead

@app.post("/leads/", response_model=schemas.Lead)
def create_new_lead(
    lead: schemas.LeadCreate, 
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user) # dependencia para proteger el endpoint
    ):
    """
    Crea un nuevo Lead en la DB
    """
    # Verficamos si el lead ya existe en la DB, evitando duplicados
    existing_lead = crud.get_lead_by_id(db, lead_id=lead.id)
    if existing_lead:
        raise HTTPException(status_code=400, detail="Lead already exists")
    # Creamos el lead
    new_lead = crud.create_lead(db, lead)
    return new_lead

@app.put("/leads/{lead_id}", response_model=schemas.Lead)
def update_lead_data(
    lead_id: str,
    lead_data: schemas.LeadUpdate,
    db: Session = Depends(get_db),
    current_user : schemas.User = Depends(get_current_user)
    ):
    """
    Actualiza un Lead
    """
    updated_lead = crud.update_lead(db, lead_id, lead_data)
    if not update_lead_data:
        raise HTTPException(status_code=404, detail="Lead not found") 
    return updated_lead

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("crm-api.main:app", host="0.0.0.0", port=8000, reload=True)
