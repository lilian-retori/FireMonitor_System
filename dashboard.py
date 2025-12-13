import streamlit as st
import pandas as pd
import time
import os
from src.config import PROCESSED_DIR, MAPS_DIR

st.set_page_config(page_title="Fogaréu Monitor", layout="wide", page_icon="🔥")

# Título e Estilo
st.title("🔥 Sistema Fogaréu - Centro de Comando")
st.markdown("Monitoramento em Tempo Real de Focos de Incêndio e Riscos Ambientais")

# Caminhos dos arquivos
CSV_PATH = os.path.join(PROCESSED_DIR, "live_monitor.csv")
MAP_PATH = os.path.join(MAPS_DIR, "mapa_risco.html")

# Função para carregar dados sem travar o app
def carregar_dados():
    if not os.path.exists(CSV_PATH):
        return None
    return pd.read_csv(CSV_PATH)

# Layout de Colunas (KPIs)
col1, col2, col3, col4 = st.columns(4)

# Container para atualização automática
placeholder = st.empty()

# Botão de atualização manual
if st.button('🔄 Atualizar Dados Agora'):
    st.rerun()

# Lógica Principal
df = carregar_dados()

if df is None:
    st.warning("⏳ Aguardando o primeiro ciclo do robô... (Execute 'python main.py' no terminal)")
else:
    # Métricas
    total_focos = len(df)
    risco_critico = len(df[df['nivel_risco'] == 'CRÍTICO'])
    temp_media = df['temp'].mean()
    fwi_max = df['FWI'].max()

    with col1:
        st.metric("Focos Ativos", total_focos, delta_color="inverse")
    with col2:
        st.metric("Alertas Críticos", risco_critico, delta="-Normal" if risco_critico == 0 else "off", delta_color="inverse")
    with col3:
        st.metric("Temp. Média Local", f"{temp_media:.1f} °C")
    with col4:
        st.metric("FWI Máximo (Risco)", f"{fwi_max:.1f}")

    # Abas
    tab1, tab2 = st.tabs(["🗺️ Mapa Operacional", "📊 Tabela de Dados"])

    with tab1:
        # Lê o HTML do mapa gerado pelo main.py e exibe no site
        if os.path.exists(MAP_PATH):
            with open(MAP_PATH, 'r', encoding='utf-8') as f:
                html_map = f.read()
            st.components.v1.html(html_map, height=600, scrolling=True)
        else:
            st.error("Mapa ainda não gerado.")

    with tab2:
        st.dataframe(df.style.highlight_max(axis=0, color='red'))

# Auto-refresh a cada 30 segundos
time.sleep(30)
st.rerun()