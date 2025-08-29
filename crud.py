# crud.py
# Este archivo contendrá las funciones para interactuar con la base de datos (Crear, Leer, Actualizar, Borrar).
# crud.py
from uuid import UUID
from sqlalchemy.orm import Session
from . import models, schemas
from passlib.context import CryptContext
from .auth import is_valid_token_and_get_email

# Instancia para el hashing de contraseñas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_user_by_email(db: Session, email: str):
    """
    Obtiene un usuario por su dirección de correo electrónico.
    """
    return db.query(models.User).filter(models.User.email == email).first()

def get_user_by_token(db:Session, token: str):
    """
    Valida un token y devuelve un usuario si éste existe
    """
    email = is_valid_token_and_get_email(token)
    if not email:
        return None
    user = get_user_by_email(db, email)
    if not user:
        return None
    return user

def create_user(db: Session, user: schemas.UserCreate, hashed_password: str):
    """
    Crea un nuevo usuario en la base de datos.
    """
    db_user = models.User(
        email=user.email,
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def authenticate_user(db: Session, email: str, password: str):
    """
    Autentica un usuario verificando su email y contraseña.
    """
    user = get_user_by_email(db, email=email)
    if not user:
        return False
    if not pwd_context.verify(password, user.hashed_password):
        return False
    return user

def get_leads(db: Session, skip: int = 0, limit: int = 100):
    """
    Obtiene una lista de leads con paginación de desplazamiento.
    """
    return db.query(models.Lead).offset(skip).limit(limit).all()

def get_lead_by_id(db: Session, lead_id: str):
    """
    Obtiene un lead por su identificador único (UUID).
    """
    return db.query(models.Lead).filter(models.Lead.id == lead_id).first()

def get_leads_count(db: Session):
    """
    Obtiene el número total de leads en la base de datos.
    """
    return db.query(models.Lead).count()

def create_lead(db: Session, lead: schemas.LeadCreate):
    """
    Crea un Lead
    """
    db_lead = models.Lead(**lead.dict())
    db.add(db_lead)
    db.commit()
    db.refresh(db_lead)
    return db_lead

def update_lead(db: Session, lead_id: str, lead_data: schemas.LeadUpdate):
    """
    Edita un Lead
    """
    db_lead = db.query(models.Lead).filter(models.Lead.id == lead_id).first()
    if not db_lead:
        return None
    # Usamos model_dump(exclude_unset=True) para obtener solo los campos que se enviaron en la petición
    update_data = lead_data.model_dump(exclude_unset=True)
    for key, value in update_data.items(): # editamos con el lead original 
        setattr(db_lead, key, value)
    # ejecutamos el update
    db.add(db_lead)
    db.commit()
    db.refresh(db_lead)
    return db_lead
