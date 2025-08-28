# crud.py
# Este archivo contendrá las funciones para interactuar con la base de datos (Crear, Leer, Actualizar, Borrar).
# crud.py
from uuid import UUID
from sqlalchemy.orm import Session
from . import models, schemas
from passlib.context import CryptContext

# Instancia para el hashing de contraseñas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_user_by_email(db: Session, email: str):
    """
    Obtiene un usuario por su dirección de correo electrónico.
    """
    return db.query(models.User).filter(models.User.email == email).first()

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