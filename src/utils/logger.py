import logging
import os


# Can't be changer once the code has run
def setup_logging():
    os.makedirs("data", exist_ok=True)
    logging.basicConfig(
        filename="data/log.txt",
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        filemode="w",
    )
