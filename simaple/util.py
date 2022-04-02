import time

from loguru import logger


class Timer:
    def __init__(self, name=""):
        self.name = name
        self.time = time.time()

    def __enter__(self):
        self.time = time.time()

    def __exit__(self, exc_type, exc_val, exc_tb):
        elapsed = time.time() - self.time
        logger.info(f"{self.name} | spent: {elapsed:.02f}s")
