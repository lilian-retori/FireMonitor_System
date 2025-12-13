
# Arquivo de Alerta Ativo).


import os
import requests
import pandas as pd
from src.ingestion import get_nasa_fire_data
from src.features import calculate_fwi
from src.modeling import FirePredictor
from src.spatial import check_fire_risk_zones

# Credenciais vindas do GitHub Secrets
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

def sentinela():
    print("--- 🛡️ INICIANDO RONDA DE VIGÍLIA ---")
    
    # 1. Coleta
    df = get_nasa_fire_data()
    if df.empty:
        print("   [STATUS] Nenhum foco ativo detectado.")
        # Opcional: enviar aviso de "Tudo Bem" para testar
        # enviar_telegram("🟢 Sistema operante. Nenhum foco detectado.")
        return

    # 2. Inteligência
    df = calculate_fwi(df)
    try:
        predictor = FirePredictor()
        df = predictor.prever_risco(df)
    except:
        df['predicao_ia_severidade'] = df['FWI'] * 0.5 # Fallback

    # 3. Decisão de Alerta
    # Regra: Alerta se Risco Crítico OU Severidade IA Alta (>80)
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
            f"🤖 **IA Severidade:** ALTA\n\n"
            f"[Acessar Painel de Comando](https://monitoramentodequeimadas.streamlit.app/)"
        )
        enviar_telegram(msg)
    else:
        print("   [STATUS] Focos detectados, mas abaixo do limiar de alerta.")

if __name__ == "__main__":
    sentinela()