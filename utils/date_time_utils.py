import re
from datetime import datetime

def get_numeric_timestamp() -> str:
    return re.sub(r"\D", "", str(datetime.now()))
