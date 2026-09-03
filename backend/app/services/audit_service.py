import json
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from datetime import datetime
from app.models.audit_model import AuditModel
from app.domain.enums import AuditEventType

class AuditService:
    @staticmethod
    def log_event(
        db: Session,
        event_type: AuditEventType | str,
        action: str,
        case_id: Optional[str] = None,
        actor: str = "SYSTEM",
        previous_state: Optional[str] = None,
        new_state: Optional[str] = None,
        reason: Optional[str] = None,
        confidence: Optional[float] = None,
        policy_rule: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> AuditModel:
        event_type_str = event_type.value if isinstance(event_type, AuditEventType) else str(event_type)
        metadata_str = json.dumps(metadata) if metadata else None

        audit_entry = AuditModel(
            case_id=case_id,
            timestamp=datetime.utcnow(),
            event_type=event_type_str,
            actor=actor,
            action=action,
            previous_state=previous_state,
            new_state=new_state,
            reason=reason,
            confidence=confidence,
            policy_rule=policy_rule,
            metadata_json=metadata_str
        )
        db.add(audit_entry)
        db.commit()
        db.refresh(audit_entry)
        return audit_entry
