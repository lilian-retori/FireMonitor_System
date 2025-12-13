import time
import os
from datetime import datetime
from src.ingestion import get_nasa_fire_data
from src.features import calculate_fwi
from src.spatial import check_fire_risk_zones
from src.modeling import FirePredictor
from src.visualization import generate_risk_map
from src.config import PROCESSED_DIR

# INTERVALO DE MONITORAMENTO (em segundos)
# Para teste agora: 60 segundos. 
# Para produção depois: 10800 (3 horas).
INTERVALO_SEGUNDOS = 60 

def ciclo_monitoramento():
    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] 🚀 INICIANDO VARREDURA...")
    
    # 1. Ingestão (Híbrida: Real ou Simulada)
    df = get_nasa_fire_data()
    
    # 2. Processamento
    df = calculate_fwi(df)
    
    # 3. Inteligência Artificial
    try:
        predictor = FirePredictor()
        df = predictor.prever_risco(df)
    except Exception as e:
        print(f"   [AVISO] IA indisponível temporariamente: {e}")

    # 4. Análise Espacial
    df_final = check_fire_risk_zones(df)
    
    # Salvar Histórico (Append mode seria ideal, mas overwrite serve por enquanto)
    df_final.to_csv(os.path.join(PROCESSED_DIR, "live_monitor.csv"), index=False)
    
    # 5. Mapa
    mapa = generate_risk_map(df_final)
    print(f"   ✅ CICLO CONCLUÍDO. Mapa atualizado em: {mapa}")

def main():
    print("=== 🔥 SENTINELA AUTOMÁTICO INICIADO ===")
    print("Pressione 'Ctrl + C' no terminal para parar o robô.\n")
    
    while True:
        try:
            ciclo_monitoramento()
            print(f"   💤 Dormindo por {INTERVALO_SEGUNDOS} segundos...")
            time.sleep(INTERVALO_SEGUNDOS)
        except KeyboardInterrupt:
            print("\n🛑 Monitoramento encerrado pelo usuário.")
            break
        except Exception as e:
            print(f"\n❌ ERRO CRÍTICO NO CICLO: {e}")
            print("   Tentando reiniciar em 10 segundos...")
            time.sleep(10)

if __name__ == "__main__":
    main()