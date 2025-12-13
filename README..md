# 🔥 FireMonitor System (Sentinela Fogaréu)

**Sistema Autônomo de Vigilância e Previsão de Incêndios Florestais.**

Este projeto é um pipeline "End-to-End" que monitora focos de calor em tempo real, calcula índices de perigo de incêndio (FWI) e utiliza Inteligência Artificial para prever a severidade de ocorrências, notificando automaticamente via Telegram em casos críticos.

---

## 🏗️ Arquitetura do Sistema

O sistema opera de forma autônoma na nuvem (Serverless) seguindo o fluxo:

1.  **Ingestão:** Satélites da NASA (MODIS/VIIRS) detectam anomalias térmicas.
2.  **Enriquecimento:** O sistema cruza as coordenadas com dados meteorológicos em tempo real (Open-Meteo).
3.  **Processamento (Physics):** Cálculo do *Fire Weather Index* (FWI) para determinar o risco físico.
4.  **Inteligência (AI):** Um modelo **CatBoost** prevê a probabilidade de severidade do incêndio.
5.  **Ação:**
    * **Crítico:** Disparo imediato de alerta para o Telegram do operador.
    * **Monitoramento:** Atualização do Dashboard público para análise visual.

---

## 📂 Estrutura de Arquivos (Onde está a inteligência?)

A lógica do sistema foi modularizada para escalabilidade:

* **`src/ingestion.py`**: Conector com APIs externas (NASA FIRMS e Open-Meteo).
* **`src/features.py`**: **(Motor Físico)** Contém a matemática dos índices de incêndio (Cálculo de FWI, temperatura, vento).
* **`src/modeling.py`**: **(Motor de IA)** Carrega o modelo treinado (`catboost_model.cbm`) para realizar inferências preditivas.
* **`src/alert.py`**: **(Sentinela)** O script executivo que orquestra a coleta, análise e decisão de enviar mensagens.
* **`dashboard.py`**: A interface visual (Frontend) construída em Streamlit.
* **`.github/workflows/sentinela.yml`**: O "coração" da automação. Define o agendamento (`cron`) para execução a cada 3 horas.

---

## 🛠️ Tecnologias Utilizadas

* **Linguagem:** Python 3.10
* **Orquestração:** GitHub Actions (CI/CD)
* **Visualização:** Streamlit Cloud
* **Machine Learning:** CatBoost
* **Dados:** NASA FIRMS, Open-Meteo API
* **Notificação:** Telegram Bot API

---

## 🚀 Como Acessar

* **Painel de Controle (Dashboard):** [Acesse aqui](https://monitoramentodequeimadas.streamlit.app/)
* **Status do Robô:** Ativo (Verificação a cada 3 horas).

---

## ⚠️ Nota de Operação

Este sistema roda 100% na nuvem.
- Não requer máquina local ligada.
- O alerta via Telegram é silencioso para riscos baixos/moderados e **ativo** apenas para riscos **CRÍTICOS**.

---
*Desenvolvido por Lilian Retori.*