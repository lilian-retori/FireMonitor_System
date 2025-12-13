import pandas as pd
import requests
import os
import time
import random
from io import StringIO
from dotenv import load_dotenv

load_dotenv()

def get_nasa_fire_data():
    """
    Busca dados na NASA. Se não encontrar nada (ou estiver sem chave),
    gera dados simulados para garantir que o pipeline de clima possa ser testado.
    """
    api_key = os.getenv("NASA_API_KEY")
    df = pd.DataFrame()

    # 1. TENTATIVA REAL (NASA)
    if api_key and not api_key.startswith("#"):
        print("   [INGESTÃO] 🛰️  Consultando satélites da NASA...")
        url = f"https://firms.modaps.eosdis.nasa.gov/api/country/csv/{api_key}/VIIRS_SNPP_NRT/BRA/1"
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                df = pd.read_csv(StringIO(response.text))
        except Exception:
            pass
    
    # 2. FALLBACK (SIMULAÇÃO) - Se a NASA falhar ou retornar 0 focos
    if df.empty:
        print("   [MODO TESTE] ⚠️  Sem dados reais (ou chave oculta). Gerando focos SIMULADOS.")
        df = _gerar_focos_simulados()
    else:
        print(f"   [SUCESSO] {len(df)} focos reais encontrados.")

    # 3. ENRIQUECIMENTO (CLIMA) - Acontece tanto para dados reais quanto simulados
    print(f"   [CLIMA] ☁️  Buscando meteorologia local (Open-Meteo) para {len(df)} pontos...")
    
    # Prepara colunas
    for col in ['temp', 'rh', 'wind', 'rain']:
        df[col] = 0.0

    for i, row in df.iterrows():
        try:
            # Consulta API de clima para a coordenada exata
            lat, lon = row['latitude'], row['longitude']
            url_w = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,relative_humidity_2m,wind_speed_10m,rain&timezone=America/Sao_Paulo"
            
            r = requests.get(url_w, timeout=5).json()['current']
            
            df.at[i, 'temp'] = r['temperature_2m']
            df.at[i, 'rh'] = r['relative_humidity_2m']
            df.at[i, 'wind'] = r['wind_speed_10m']
            df.at[i, 'rain'] = r['rain']
            
            # Barra de progresso visual simples (.)
            print(".", end="", flush=True)
            time.sleep(0.2) # Respeitar limites da API gratuita
        except:
            print("x", end="", flush=True)
            # Em caso de falha no clima, usa valores médios seguros
            df.at[i, 'temp'] = 30.0; df.at[i, 'rh'] = 50.0; df.at[i, 'wind'] = 10.0
            
    print("\n   -> Dados climáticos integrados.")
    return df

def _gerar_focos_simulados():
    """Gera 5 pontos aleatórios no Pará para teste"""
    dados = {
        'latitude': [-3.4, -4.5, -3.8, -6.2, -5.1],
        'longitude': [-52.0, -53.1, -52.5, -50.0, -51.5],
        'brightness': [350, 310, 380, 330, 360],
        'acq_date': ['2025-10-01'] * 5
    }
    return pd.DataFrame(dados)