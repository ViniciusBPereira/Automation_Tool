import logging
import os
import time

# Define nível de log pelo ambiente (default: INFO)
log_level = os.getenv("LOG_LEVEL", "INFO").upper()

# Handler para console (apenas terminal)
console_handler = logging.StreamHandler()
console_handler.setLevel(getattr(logging, log_level, logging.INFO))

# Formato do log
formatter = logging.Formatter(
    "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)

# Força uso de UTC (troque para time.localtime se preferir horário local)
logging.Formatter.converter = time.gmtime

console_handler.setFormatter(formatter)

# Configuração final
logging.basicConfig(
    level=getattr(logging, log_level, logging.INFO),
    handlers=[console_handler]
)

# Logger principal
logger = logging.getLogger("DataExport")
