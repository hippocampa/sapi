import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Optional: Add a console handler or file handler if needed
console_handler = logging.StreamHandler()
console_handler.setFormatter(
    logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
)
logger.addHandler(console_handler)
