from fastapi import FastAPI, Depends, HTTPException, status, Query
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy.sql import text
from .database import get_db
from passlib.context import CryptContext

from . import models, schemas, crud, auth
from .database import get_db

app = FastAPI()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Endpoint para verificar la conexión a la base de datos
@app.get("/health")
def check_db_connection(db: Session = Depends(get_db)):
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
def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
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
    user = crud.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = auth.create_access_token(data={"sub": user.email})
    
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/leads", response_model=schemas.PaginatedLeads)
def read_leads(
    db: Session = Depends(get_db),
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
def read_lead_by_id(lead_id: str, db: Session = Depends(get_db)):
    """
    Obtiene un lead específico por su ID.
    """
    lead = crud.get_lead_by_id(db, lead_id=lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    return lead

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("crm-api.main:app", host="0.0.0.0", port=8000, reload=True)
