# schemas.py
from datetime import datetime
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel
import enum

# Define el ENUM para los estados del lead
class Status(str, enum.Enum):
    contacted = "contacted"
    responded = "responded"
    completed = "completed"
    quoted = "quoted"


class UserCreate(BaseModel):
    username: str
    password: str

class User(BaseModel):
    id: UUID
    username: str
    is_active: bool
    
    class Config:
        from_attributes = True

# --- Modelos de Leads ---

class LeadBase(BaseModel):
    is_active: Optional[bool] = None
    origin: Optional[str] = None
    conversation_state: Optional[dict] = None
    current_step: Optional[str] = None
    collected_data: Optional[dict] = None
    previous_step: Optional[str] = None
    name: Optional[str] = None
    status: Optional[Status] = None

class LeadCreate(LeadBase):
    id: str

class Lead(LeadBase):
    id: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class LeadUpdate(BaseModel):
    is_active: Optional[bool] = None
    name: Optional[str] = None
    status: Optional[Status] = None

    class Config:
        from_attributes = True

# --- Modelos de Paginación ---

class PaginatedLeads(BaseModel):
    total: int
    leads: List[Lead]