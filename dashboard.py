import streamlit as st
import pandas as pd
import pydeck as pdk
import numpy as np
import os  # <--- O import deve ficar aqui em cima, garantido.

# 1. Configuração da Página (Título e Ícone)
st.set_page_config(
    page_title="Sistema Sentinela - Monitoramento SP",
    page_icon="🔥",
    layout="wide"
)

# 2. Função de Carga de Dados
@st.cache_data
def carregar_dados():
    # Tenta carregar o arquivo oficial (Gigante - Local)
    arquivos_possiveis = [
        "data/focos_br_todos-sats_2024.csv",
        "data/focos_queimadas.csv",
        "data/dados_final.csv"
    ]
    
    arquivo_oficial = None
    for arq in arquivos_possiveis:
        if os.path.exists(arq):
            arquivo_oficial = arq
            break
            
    # Caminho da amostra (Pequena - Nuvem)
    arquivo_amostra = "data/sample_dados_brutos.csv" 
    
    if arquivo_oficial and os.path.exists(arquivo_oficial):
        return pd.read_csv(arquivo_oficial)
    elif os.path.exists(arquivo_amostra):
        st.warning("⚠️ Atenção: Rodando em modo Nuvem (Dados de Amostra).")
        return pd.read_csv(arquivo_amostra)
    else:
        st.error("❌ Erro Crítico: Nenhum dado encontrado na pasta 'data'.")
        return pd.DataFrame()

# ==========================================
# 3. INTERFACE PRINCIPAL
# ==========================================

st.title("🔥 Sistema Sentinela: Monitoramento de Queimadas (SP)")
st.markdown("---")

# Carrega os dados
df = carregar_dados()

if not df.empty:
    # --- PRÉ-PROCESSAMENTO RÁPIDO ---
    # Descobre a coluna de latitude/longitude
    col_lat = 'latitude' if 'latitude' in df.columns else None
    col_lon = 'longitude' if 'longitude' in df.columns else None
    
    # Se não achar, tenta limpar nomes
    if not col_lat:
        for col in df.columns:
            if 'lat' in col.lower(): col_lat = col
            if 'lon' in col.lower(): col_lon = col

    # Filtra para garantir que tem coordenadas
    if col_lat and col_lon:
        df = df.dropna(subset=[col_lat, col_lon])
        
        # --- FILTRO LATERAL ---
        st.sidebar.header("Filtros")
        
        # Filtro de Estado
        col_estado = None
        for col in df.columns:
            if 'estado' in col.lower() or 'uf' in col.lower():
                col_estado = col
                break
        
        if col_estado:
            estados = df[col_estado].unique()
            selecao_estado = st.sidebar.multiselect("Estado", options=estados, default=estados)
            if selecao_estado:
                df_filtrado = df[df[col_estado].isin(selecao_estado)]
            else:
                df_filtrado = df
        else:
            df_filtrado = df

        # --- KPI's (Métricas) ---
        col1, col2, col3 = st.columns(3)
        col1.metric("Focos Detectados", len(df_filtrado))
        
        if 'frp' in df_filtrado.columns:
            frp_medio = df_filtrado['frp'].mean()
            col2.metric("Intensidade Média (FRP)", f"{frp_medio:.1f}")
        else:
            col2.metric("Status", "Monitorando")

        col3.metric("Região", "São Paulo (Foco)")

        # --- O MAPA CORRIGIDO (FOCA EM SP) ---
        st.subheader("📍 Mapa de Calor e Focos")
        
        layer = pdk.Layer(
            "ScatterplotLayer",
            data=df_filtrado,
            get_position=[col_lon, col_lat],
            get_color=[255, 80, 80, 200],
            get_radius=2000,
            pickable=True
        )

        view_state = pdk.ViewState(
            latitude=-22.5,    # Centro de SP
            longitude=-48.0,   # Centro de SP
            zoom=6,
            pitch=50,
        )

        r = pdk.Deck(
            layers=[layer],
            initial_view_state=view_state,
            tooltip={"text": "Foco de Incêndio Detectado"}
        )
        st.pydeck_chart(r)

        # --- GRÁFICO TEMPORAL ---
        st.subheader("📈 Evolução Temporal")
        
        col_data = None
        possiveis_datas = ['datahora', 'data_pas', 'acq_date', 'Data', 'data']
        for col in df.columns:
            if col in possiveis_datas:
                col_data = col
                break
        
        if col_data:
            df_filtrado['data_temp'] = pd.to_datetime(df_filtrado[col_data]).dt.date
            focos_por_dia = df_filtrado.groupby('data_temp').size()
            st.line_chart(focos_por_dia)
        else:
            st.info("Coluna de data não identificada para gerar gráfico temporal.")

    else:
        st.error("Erro: Colunas de Latitude/Longitude não encontradas no arquivo.")
else:
    st.warning("Aguardando dados...")