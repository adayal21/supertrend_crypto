import logging
import os

os.makedirs("logs", exist_ok=True)

logger = logging.getLogger("crypto_trader")

logger.setLevel(logging.INFO)

formatter = logging.Formatter(
    "%(asctime)s | %(levelname)s | %(message)s"
)

# ==========================================================
# FILE HANDLER (DETAILED LOGS)
# ==========================================================

file_handler = logging.FileHandler(
    "logs/system.log"
)

file_handler.setLevel(logging.INFO)

file_handler.setFormatter(formatter)

# ==========================================================
# CONSOLE HANDLER (MINIMAL LOGS)
# ==========================================================

console_handler = logging.StreamHandler()

console_handler.setLevel(logging.WARNING)

console_handler.setFormatter(formatter)

# ==========================================================
# PREVENT DUPLICATE HANDLERS
# ==========================================================

if not logger.handlers:

    logger.addHandler(file_handler)

    logger.addHandler(console_handler)