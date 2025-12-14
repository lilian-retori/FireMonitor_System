import pandas as pd
import os

# Nomes dos seus arquivos gigantes (ajuste os nomes!)
arquivo1 = "data/nome_do_arquivo_gigante_1.csv"

try:
    print("Lendo as primeiras 1000 linhas...")
    # Lê só o topo do arquivo
    df = pd.read_csv(arquivo1, nrows=1000)
    
    # Salva uma versão mini
    df.to_csv("data/sample_dados_brutos.csv", index=False)
    print("✅ Sucesso! Arquivo 'data/sample_dados_brutos.csv' criado.")
    print("Pode subir este arquivo pequeno para o GitHub.")
    
except Exception as e:
    print(f"Erro: {e}")