import pandas as pd
import numpy as np
from catboost import CatBoostRegressor
import os
from .config import MODELS_DIR

class FirePredictor:
    def __init__(self):
        self.model = None
        # Agora buscamos o arquivo .cbm (Formato nativo do CatBoost)
        self.model_path = os.path.join(MODELS_DIR, "catboost_fire_v2.cbm")
    
    def carregar(self):
        """Carrega o cérebro da IA do disco para a memória."""
        if os.path.exists(self.model_path):
            self.model = CatBoostRegressor()
            self.model.load_model(self.model_path)
        else:
            raise FileNotFoundError(f"MODELO NÃO ENCONTRADO: {self.model_path}. Execute 'python train_brain.py' primeiro.")

    def prever_risco(self, df):
        """
        Recebe dados do satélite + clima e prevê a severidade (0-100).
        """
        if self.model is None:
            self.carregar()
            
        # Preparar as colunas exatas que o modelo espera
        features_necessarias = ['temp', 'rh', 'wind', 'rain', 'FWI']
        
        # Validação de segurança: garantir que as colunas existem
        for col in features_necessarias:
            if col not in df.columns:
                df[col] = 0.0
                
        dados_entrada = df[features_necessarias]
        
        # Inferência (A mágica acontece aqui)
        preds = self.model.predict(dados_entrada)
        
        # Salva no DataFrame (garantindo que não passe de 100 nem seja negativo)
        df['predicao_ia_severidade'] = np.clip(preds, 0, 100)
        
        return df