import json
import logging
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

def audit_event(event, details=None):
    record = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "event": str(event),
        "details": details or {},
    }
    logger.info("AGENT_AUDIT %s", json.dumps(record, ensure_ascii=False, default=str))
    return record
