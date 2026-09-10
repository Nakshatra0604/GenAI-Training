import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

VECTOR_STORE_PATH = Path("vector_store")

def get_generation_model():
    return os.getenv("GENERATION_MODEL")

def check_generation_readiness():

    generation_model =  get_generation_model()

    if generation_model:
        return "ready"

    return "not_ready"


def check_vector_store_readiness():

    if VECTOR_STORE_PATH.exists():
        return "ready"

    return "not_ready"






    


