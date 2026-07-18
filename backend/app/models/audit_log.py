from pydantic import BaseModel


class AuditLog(BaseModel):
    audit_id: str
    action: str
    entity_type: str
    entity_id: str

