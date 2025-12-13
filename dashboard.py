import streamlit as st
import pandas as pd
import os
from src.config import PROCESSED_DIR, MAPS_DIR
# Importando as ferramentas do robô
from src.ingestion import get_nasa_fire_data
from src.features import calculate_fwi
from src.spatial import check_fire_risk_zones
from src.modeling import FirePredictor
from src.visualization import generate_risk_map

st.set_page_config(page_title="Sentinela Ar Monitor", layout="wide", page_icon="🔥")

# --- FUNÇÃO DO ROBÔ (Injetada no Site) ---
def rodar_ciclo_na_nuvem():
    """Executa o pipeline completo sob demanda."""
    status = st.status("📡 Conectando aos satélites...", expanded=True)
    
    try:
        # 1. Ingestão
        status.write("Baixando dados NASA e Clima...")
        df = get_nasa_fire_data()
        
        if df.empty:
            status.update(label="⚠️ Nenhum foco encontrado.", state="error")
            return None

        # 2. Processamento
        status.write("Calculando física do fogo (FWI)...")
        df = calculate_fwi(df)

        # 3. Inteligência Artificial
        status.write("Consultando Cérebro IA (CatBoost)...")
        try:
            predictor = FirePredictor()
            df = predictor.prever_risco(df)
        except Exception as e:
            status.write(f"⚠️ IA Indisponível (Usando cálculo simples): {e}")
            # Fallback simples se o modelo não subiu
            df['predicao_ia_severidade'] = df['FWI'] * 0.5 

        # 4. Mapa
        status.write("Gerando mapas de risco...")
        df_final = check_fire_risk_zones(df)
        generate_risk_map(df_final)
        
        # Salvar para cache
        os.makedirs(PROCESSED_DIR, exist_ok=True)
        csv_path = os.path.join(PROCESSED_DIR, "live_monitor.csv")
        df_final.to_csv(csv_path, index=False)
        
        status.update(label="✅ Dados Atualizados com Sucesso!", state="complete")
        return df_final
        
    except Exception as e:
        status.update(label=f"❌ Erro Crítico: {str(e)}", state="error")
        return None

# --- INTERFACE VISUAL ---
st.title("🔥 Sistema Sentinela do Ar - Monitoramento Nuvem")

# Botão para Forçar Atualização
if st.button('🔄 Executar Varredura Agora'):
    rodar_ciclo_na_nuvem()
    st.rerun()

# Tenta carregar dados existentes
CSV_PATH = os.path.join(PROCESSED_DIR, "live_monitor.csv")
MAP_PATH = os.path.join(MAPS_DIR, "mapa_risco.html")

if os.path.exists(CSV_PATH):
    df = pd.read_csv(CSV_PATH)
else:
    st.warning("Arquivo de dados não encontrado. Iniciando primeira varredura automática...")
    df = rodar_ciclo_na_nuvem()

# Se depois de tudo ainda não tiver dados (API falhou ou 0 focos)
if df is None or df.empty:
    st.error("Não há dados para exibir no momento. Tente novamente mais tarde.")
    st.stop()

# --- DASHBOARD (Só exibe se tiver dados) ---
col1, col2, col3, col4 = st.columns(4)
with col1: st.metric("Focos Ativos", len(df))
with col2: st.metric("Risco Crítico", len(df[df['nivel_risco'] == 'CRÍTICO']))
with col3: st.metric("Temp. Média", f"{df['temp'].mean():.1f} °C")
with col4: st.metric("IA Severidade Máx", f"{df.get('predicao_ia_severidade', df['FWI']).max():.1f}")

tab1, tab2 = st.tabs(["🗺️ Mapa", "📊 Dados"])
with tab1:
    if os.path.exists(MAP_PATH):
        with open(MAP_PATH, 'r', encoding='utf-8') as f:
            st.components.v1.html(f.read(), height=600)
with tab2:
    st.dataframe(df)