import re
from datetime import datetime

def get_numeric_timestamp() -> str:
    """Função para retornar a data e hora atual em forma de str, ex: 2026-07-27:00:00:00 -> 20260727000000.
    
    :return: str(20260727000000).
    """
    return re.sub(r"\D", "", str(datetime.now()))

def date_str_to_int(date_time_str: str) -> tuple:
    """Função para transformar uma data "27/07/2026" -> (27, 7, 2026).
    
    :param date_time_str: Parâmetro de data formato str, ex: "27/07/2026".
    :return: (27, 7, 2026).
    """
    date_split = date_time_str.split("/")
    return int(date_split[0]), int(date_split[1]), int(date_split[2])
