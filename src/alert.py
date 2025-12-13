import os
import requests
import pandas as pd
import numpy as np
from src.ingestion import get_nasa_fire_data
from src.features import calculate_fwi
from src.modeling import FirePredictor

# Credenciais
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def enviar_telegram(mensagem):
    if not TELEGRAM_TOKEN or not CHAT_ID:
        print("   [ERRO] Credenciais do Telegram ausentes.")
        return
    
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID, 
        "text": mensagem, 
        "parse_mode": "Markdown"
    }
    try:
        requests.post(url, json=payload, timeout=10)
        print("   [SUCESSO] Mensagem enviada.")
    except Exception as e:
        print(f"   [FALHA] Erro no envio: {e}")

def classificar_risco(fwi):
    # Regra de Negócio Simples para garantir que a coluna exista
    if fwi > 50:
        return 'CRÍTICO'
    elif fwi > 20:
        return 'ALTO'
    else:
        return 'MODERADO'

def sentinela():
    print("--- 🛡️ INICIANDO RONDA DE VIGÍLIA ---")
    
    # 1. Coleta
    df = get_nasa_fire_data()
    
    # Proteção contra tabela vazia
    if df.empty:
        print("   [STATUS] Nenhum foco ativo detectado (Tabela Vazia).")
        return

    # 2. Inteligência (Cálculo do FWI)
    df = calculate_fwi(df)

    # 3. Blindagem (Garantir que a coluna nivel_risco exista)
    if 'nivel_risco' not in df.columns:
        print("   [AVISO] Coluna nivel_risco ausente. Calculando agora...")
        df['nivel_risco'] = df['FWI'].apply(classificar_risco)

    # 4. Predição IA (Opcional, com fallback)
    try:
        predictor = FirePredictor()
        df = predictor.prever_risco(df)
    except:
        # Se a IA falhar, usa regra simples baseada no FWI
        df['predicao_ia_severidade'] = df['FWI'] * 0.8 

    # 5. Decisão de Alerta
    # Regra: Alerta se Risco for CRÍTICO OU Severidade IA > 80
    risco_alto = df[
        (df['nivel_risco'] == 'CRÍTICO') | 
        (df['predicao_ia_severidade'] > 80)
    ]

    if not risco_alto.empty:
        qtd = len(risco_alto)
        max_fwi = risco_alto['FWI'].max()
        
        msg = (
            f"🚨 **ALERTA DE FOGO: {qtd} FOCOS CRÍTICOS** 🚨\n\n"
            f"🔥 **FWI Máximo:** {max_fwi:.1f}\n"
            f"⚠️ **Nível:** CRÍTICO\n\n"
            f"[Acessar Painel de Comando](https://monitoramentodequeimadas.streamlit.app/)"
        )
        enviar_telegram(msg)
    else:
        print("   [STATUS] Focos analisados. Nenhum atingiu o limiar de alerta.")

if __name__ == "__main__":
    sentinela()