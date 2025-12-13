import os
from pathlib import Path

# Definindo a raiz do projeto automaticamente
ROOT_DIR = Path(__file__).parent.parent
DATA_DIR = ROOT_DIR / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
MAPS_DIR = DATA_DIR / "maps"
MODELS_DIR = DATA_DIR / "models"  # <--- ESTA LINHA FALTAVA

# Cria as pastas se não existirem
os.makedirs(RAW_DIR, exist_ok=True)
os.makedirs(PROCESSED_DIR, exist_ok=True)
os.makedirs(MAPS_DIR, exist_ok=True)
os.makedirs(MODELS_DIR, exist_ok=True)

# Chave da NASA (Troque pela sua real depois)
NASA_API_KEY = os.getenv("NASA_API_KEY", "DEMO_KEY")