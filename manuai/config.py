import os
import random
from dataclasses import dataclass
from enum import Enum
from pathlib import Path


class ModelProvider(str, Enum):
    OLLAMA = "ollama"


@dataclass
class ModelConfig:
    name: str
    temperature: float
    provider: ModelProvider


# Default models using Ollama
LLAMA_3_1 = ModelConfig("llama3.1:8b", 0.0, ModelProvider.OLLAMA)
MISTRAL_7B = ModelConfig("mistral:7b", 0.0, ModelProvider.OLLAMA)


class Config:
    SEED = 42
    MODEL = LLAMA_3_1
    COMPLEX_MODEL = MISTRAL_7B

    class Path:
        APP_HOME = Path(os.getenv("APP_HOME", Path(__file__).parent.parent))
        DATA_DIR = APP_HOME / "data"
        DATABASE_PATH = DATA_DIR / "ecommerce.sqlite"


def seed_everything(seed: int = Config.SEED):
    random.seed(seed)
