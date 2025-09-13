from datetime import datetime, date
from typing import Dict, Any

def serialize_employee(doc: Dict[str, Any]) -> Dict[str, Any]:

    if not doc:
        return doc
    output = dict(doc)  
    output.pop("_id", None)
    jd = output.get("joining_date")
    if isinstance(jd, (datetime, date)):
        # if datetime -> isoformat; if date -> isoformat
        output["joining_date"] = jd.isoformat()
    return output
