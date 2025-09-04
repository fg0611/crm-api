
# Define el ENUM para los estados del lead
import enum

class Status(str, enum.Enum):
    contacted = "contacted"
    responded = "responded"
    completed = "completed"
    quoted = "quoted"
    signed = "signed"