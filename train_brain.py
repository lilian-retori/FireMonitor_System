import pandas as pd
import numpy as np
from catboost import CatBoostRegressor
import os
from src.config import MODELS_DIR

def treinar_novo_cerebro():
    print("🧠 INICIANDO TREINAMENTO NEURAL (CatBoost)...")
    
    # 1. Gerar Cenários Baseados em Física (Knowledge Distillation)
    # Criamos 5000 situações possíveis de clima
    n_samples = 5000
    np.random.seed(42)
    
    data = {
        'temp': np.random.uniform(20, 45, n_samples),  # 20°C a 45°C
        'rh': np.random.uniform(10, 90, n_samples),    # 10% a 90% umidade
        'wind': np.random.uniform(0, 40, n_samples),   # 0 a 40 km/h vento
        'rain': np.random.choice([0, 0, 0, 0, 5, 20], n_samples) # Maioria sem chuva
    }
    df = pd.DataFrame(data)
    
    # 2. Calcular o FWI para esses cenários (A "Verdade" Física)
    # Fórmula simplificada do Índice Canadense
    df['FFMC'] = 59.5 * (250 - df['rh']) / (147.2 + df['temp'])
    df['ISI'] = 0.208 * df['wind'] * (1 - np.exp(-0.98 * df['FFMC']))
    df['FWI'] = df['ISI'] * 1.5
    
    # 3. Definir a "Severidade" (Target)
    # A severidade real é uma combinação complexa. Vamos ensinar isso à IA.
    # Severidade aumenta com FWI, mas explode com Vento forte.
    df['severidade_real'] = (
        (df['FWI'] * 0.6) + 
        (df['wind'] * 1.5) + 
        (df['temp'] * 0.5) - 
        (df['rain'] * 10)
    )
    
    # Normalizar para 0-100
    df['severidade_real'] = np.clip(df['severidade_real'], 0, 100)
    
    print(f"   -> {n_samples} cenários físicos gerados.")
    print("   -> Ensinando padrões ao CatBoost...")

    # 4. Treinar o CatBoost
    # Features que o modelo vai ver no mundo real
    X = df[['temp', 'rh', 'wind', 'rain', 'FWI']]
    y = df['severidade_real']
    
    model = CatBoostRegressor(
        iterations=500, 
        depth=6, 
        learning_rate=0.1, 
        loss_function='RMSE',
        verbose=False
    )
    
    model.fit(X, y)
    
    # 5. Salvar o Cérebro (.cbm)
    caminho_modelo = os.path.join(MODELS_DIR, "catboost_fire_v2.cbm")
    model.save_model(caminho_modelo)
    
    print(f"✅ CÉREBRO SALVO COM SUCESSO EM:\n   {caminho_modelo}")

if __name__ == "__main__":
    treinar_novo_cerebro()