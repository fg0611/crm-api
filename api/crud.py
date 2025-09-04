# crud.py
# Este archivo contendrá las funciones para interactuar con la base de datos (Crear, Leer, Actualizar, Borrar).
# crud.py
from typing import Optional
from uuid import UUID
from sqlalchemy import func
from sqlalchemy.orm import Session
from . import models, schemas
from passlib.context import CryptContext
from .auth import is_valid_token_and_get_username

# Instancia para el hashing de contraseñas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_user_by_username(db: Session, username: str):
    """
    Obtiene un usuario por su dirección de correo electrónico.
    """
    return db.query(models.User).filter(models.User.username == username).first()

def get_user_by_token(db:Session, token: str):
    """
    Valida un token y devuelve un usuario si éste existe
    """
    username = is_valid_token_and_get_username(token)
    if not username:
        return None
    user = get_user_by_username(db, username)
    if not user:
        return None
    return user

def create_user(db: Session, user: schemas.UserCreate, hashed_password: str):
    """
    Crea un nuevo usuario en la base de datos.
    """
    db_user = models.User(
        username=user.username,
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def authenticate_user(db: Session, username: str, password: str):
    """
    Autentica un usuario verificando su username y contraseña.
    """
    user = get_user_by_username(db, username=username)
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

# Función para obtener los leads con filtros
def get_leads(
    db: Session, 
    skip: int = 0, 
    limit: int = 100,
    lead_id: Optional[str] = None,
    name: Optional[str] = None,
    is_active: Optional[bool] = None,
    status: Optional[str] = None,
    collected_data_key: Optional[str] = None,
    collected_data_value: Optional[str] = None,
):
    """
    Obtiene una lista de leads con paginación y filtros.
    """
    query = db.query(models.Lead)
    
    # Aplicar filtros si existen
    if lead_id:
        query = query.filter(models.Lead.id.like(f"%{lead_id}"))
    if name:
        query = query.filter(func.lower(models.Lead.name).like(f"%{name.lower()}%"))
    if is_active is not None:
        query = query.filter(models.Lead.is_active == is_active)
    if status:
        query = query.filter(models.Lead.status == status)
    
    # Filtro para collected_data (asumiendo que es un campo de tipo JSONB)
    if collected_data_key and collected_data_value:
        query = query.filter(models.Lead.collected_data[collected_data_key].astext == collected_data_value)

    return query.offset(skip).limit(limit).all()


# Función para obtener el recuento total de leads filtrados
def get_filtered_leads_count(
    db: Session,
    lead_id: Optional[str] = None,
    name: Optional[str] = None,
    is_active: Optional[bool] = None,
    status: Optional[str] = None,
    collected_data_key: Optional[str] = None,
    collected_data_value: Optional[str] = None,
):
    """
    Obtiene el número total de leads que coinciden con los filtros.
    """
    query = db.query(models.Lead)
    
    if lead_id:
        query = query.filter(models.Lead.id == lead_id)
    if name:
        query = query.filter(func.lower(models.Lead.name).like(f"%{name.lower()}%"))
    if is_active is not None:
        query = query.filter(models.Lead.is_active == is_active)
    if status:
        query = query.filter(models.Lead.status == status)
    
    if collected_data_key and collected_data_value:
        query = query.filter(models.Lead.collected_data[collected_data_key].astext == collected_data_value)
    
    return query.count()