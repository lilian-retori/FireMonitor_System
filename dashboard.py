import streamlit as st
import pandas as pd
import pydeck as pdk
import io
import os

# 1. Configuração da Página
st.set_page_config(
    page_title="Sistema Sentinela - Monitoramento SP",
    page_icon="🔥",
    layout="wide"
)

# 2. Dados Embarcados (Garantia de Funcionamento na Apresentação)
DADOS_EMERGENCIA = """latitude,longitude,datahora,frp,estado,municipio
-22.905,-47.061,2024-08-25,15.5,SAO PAULO,CAMPINAS
-21.170,-47.810,2024-08-25,22.1,SAO PAULO,RIBEIRAO PRETO
-23.550,-46.633,2024-08-26,10.2,SAO PAULO,SAO PAULO
-22.120,-51.380,2024-08-26,45.3,SAO PAULO,PRESIDENTE PRUDENTE
-20.530,-47.400,2024-08-27,30.5,SAO PAULO,FRANCA
-23.180,-46.890,2024-08-27,12.8,SAO PAULO,JUNDIAI
-22.310,-49.070,2024-08-28,18.4,SAO PAULO,BAURU
-21.790,-48.170,2024-08-28,25.6,SAO PAULO,ARARAQUARA
-23.960,-46.330,2024-08-29,11.0,SAO PAULO,SANTOS
-22.730,-47.640,2024-08-29,14.2,SAO PAULO,PIRACICABA
-23.110,-46.550,2024-08-30,19.1,SAO PAULO,ATIBAIA
-22.400,-47.560,2024-08-30,13.5,SAO PAULO,RIO CLARO
-23.030,-45.550,2024-08-31,28.9,SAO PAULO,TAUBATE
-21.800,-49.200,2024-09-01,16.7,SAO PAULO,LINS
-20.810,-49.370,2024-09-01,33.2,SAO PAULO,SAO JOSE DO RIO PRETO"""

@st.cache_data
def carregar_dados():
    # Tenta ler arquivo local primeiro (seu PC)
    arquivo_local = "data/focos_br_todos-sats_2024.csv"
    
    if os.path.exists(arquivo_local):
        return pd.read_csv(arquivo_local)
    else:
        # Se falhar (Nuvem), usa os dados chumbados acima
        st.warning("⚠️ Modo de Apresentação (Dados Simulados/Amostra)")
        return pd.read_csv(io.StringIO(DADOS_EMERGENCIA))

# ==========================================
# 3. INTERFACE PRINCIPAL
# ==========================================
st.title("🔥 Sistema Sentinela: Monitoramento de Queimadas (SP)")
st.markdown("---")

df = carregar_dados()

if not df.empty:
    # Garante colunas numéricas
    df['latitude'] = pd.to_numeric(df['latitude'], errors='coerce')
    df['longitude'] = pd.to_numeric(df['longitude'], errors='coerce')
    df = df.dropna(subset=['latitude', 'longitude'])

    # --- FILTRO ---
    st.sidebar.header("Filtros")
    cidades = df['municipio'].unique()
    sel_cidade = st.sidebar.multiselect("Município", cidades, default=cidades)
    
    if sel_cidade:
        df_filtrado = df[df['municipio'].isin(sel_cidade)]
    else:
        df_filtrado = df

    # --- KPI's ---
    col1, col2, col3 = st.columns(3)
    col1.metric("Focos Ativos", len(df_filtrado))
    col2.metric("Intensidade Máx (FRP)", f"{df_filtrado['frp'].max():.1f}")
    col3.metric("Status", "Monitorando SP")

    # --- MAPA (Focado em SP) ---
    st.subheader("📍 Mapa de Calor e Risco")
    
    layer = pdk.Layer(
        "ScatterplotLayer",
        data=df_filtrado,
        get_position=['longitude', 'latitude'],
        get_color=[255, 50, 50, 200], # Vermelho
        get_radius=15000, # Raio visível
        pickable=True
    )

    view_state = pdk.ViewState(
        latitude=-22.5,
        longitude=-48.0,
        zoom=6,
        pitch=40
    )

    r = pdk.Deck(
        layers=[layer],
        initial_view_state=view_state,
        tooltip={"text": "{municipio}\nFRP: {frp}"}
    )
    st.pydeck_chart(r)
    
    # --- DADOS ---
    with st.expander("Ver Tabela de Dados"):
        st.dataframe(df_filtrado)

else:
    st.error("Erro fatal: Dados não carregaram.")