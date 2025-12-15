import streamlit as st
import pandas as pd
import pydeck as pdk
import io
import os
import requests # <--- Biblioteca necessária para o Telegram

# 1. Configuração da Página
st.set_page_config(
    page_title="Sistema Sentinela - Monitoramento SP",
    page_icon="🔥",
    layout="wide"
)

# ==========================================
# FUNÇÕES DE BACKEND (Telegram e Dados)
# ==========================================

def enviar_telegram(token, chat_id, mensagem):
    try:
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        data = {"chat_id": chat_id, "text": mensagem}
        response = requests.post(url, data=data)
        return response.json()
    except Exception as e:
        return {"ok": False, "description": str(e)}

# Dados "Chumbados" para garantir funcionamento na apresentação
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
    arquivo_local = "data/focos_br_todos-sats_2024.csv"
    if os.path.exists(arquivo_local):
        return pd.read_csv(arquivo_local)
    else:
        return pd.read_csv(io.StringIO(DADOS_EMERGENCIA))

# ==========================================
# INTERFACE PRINCIPAL
# ==========================================
st.title("🔥 Sistema Sentinela: Monitoramento de Queimadas (SP)")
st.markdown("---")

# --- BARRA LATERAL (Configuração do Bot) ---
st.sidebar.header("📡 Configuração de Alertas")
st.sidebar.info("Insira as credenciais para ativar o envio.")
bot_token = st.sidebar.text_input("Token do Bot (Telegram)", type="password")
chat_id = st.sidebar.text_input("Chat ID (Seu ID)")

# Botão de Teste Manual
if st.sidebar.button("🔔 Testar Disparo Manual"):
    if bot_token and chat_id:
        resp = enviar_telegram(bot_token, chat_id, "🚨 TESTE: O Sistema Sentinela está ativo e monitorando SP!")
        if resp.get("ok"):
            st.sidebar.success("Mensagem enviada!")
        else:
            st.sidebar.error(f"Erro: {resp}")
    else:
        st.sidebar.warning("Preencha o Token e o Chat ID primeiro.")

# --- LÓGICA DO DASHBOARD ---
df = carregar_dados()

if not df.empty:
    df['latitude'] = pd.to_numeric(df['latitude'], errors='coerce')
    df['longitude'] = pd.to_numeric(df['longitude'], errors='coerce')
    df = df.dropna(subset=['latitude', 'longitude'])

    # Filtros
    st.sidebar.markdown("---")
    st.sidebar.header("Filtros de Mapa")
    cidades = df['municipio'].unique()
    sel_cidade = st.sidebar.multiselect("Município", cidades, default=cidades)
    
    if sel_cidade:
        df_filtrado = df[df['municipio'].isin(sel_cidade)]
    else:
        df_filtrado = df

    # KPI's
    col1, col2, col3 = st.columns(3)
    qtd_focos = len(df_filtrado)
    col1.metric("Focos Ativos", qtd_focos)
    col2.metric("Intensidade Máx (FRP)", f"{df_filtrado['frp'].max():.1f}")
    
    status = "Crítico" if qtd_focos > 5 else "Normal"
    col3.metric("Status", status)

    # --- LÓGICA AUTOMÁTICA DE ALERTA ---
    # Se o status for crítico E o usuário preencheu o bot, avisa automaticamente
    if status == "Crítico" and bot_token and chat_id:
        if st.button("⚠️ ALERTA: Situação Crítica Detectada - ENVIAR RELATÓRIO"):
            msg = f"🚨 ALERTA DE INCÊNDIO (SP)\n\nSituação: CRÍTICA\nFocos Ativos: {qtd_focos}\nCidades Afetadas: {', '.join(df_filtrado['municipio'].unique()[:3])}..."
            enviar_telegram(bot_token, chat_id, msg)
            st.success("Relatório de crise enviado para a Defesa Civil (Telegram).")

    # MAPA
    st.subheader("📍 Monitoramento em Tempo Real")
    layer = pdk.Layer(
        "ScatterplotLayer",
        data=df_filtrado,
        get_position=['longitude', 'latitude'],
        get_color=[255, 50, 50, 200],
        get_radius=15000,
        pickable=True
    )
    view_state = pdk.ViewState(latitude=-22.5, longitude=-48.0, zoom=6, pitch=40)
    r = pdk.Deck(layers=[layer], initial_view_state=view_state, tooltip={"text": "{municipio}\nFRP: {frp}"})
    st.pydeck_chart(r)
    
    with st.expander("Ver Dados Brutos"):
        st.dataframe(df_filtrado)

else:
    st.error("Erro fatal: Dados não carregaram.")