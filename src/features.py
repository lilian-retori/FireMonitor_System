import numpy as np
import math

def calculate_fwi(df):
    """
    Aplica cálculo simplificado do índice FWI canadense.
    """
    df = df.copy()
    
    # Fórmulas simplificadas para demonstração baseadas no script PrevisãoQueimadas
    # FFMC: Fine Fuel Moisture Code (Inflamabilidade)
    df['FFMC'] = 59.5 * (250 - df['rh']) / (147.2 + df['temp'])
    
    # ISI: Initial Spread Index (Velocidade de propagação)
    # Combinando Vento + FFMC
    df['ISI'] = 0.208 * df['wind'] * (1 - math.e ** (-0.98 * df['FFMC']))
    
    # FWI Final (Risco combinado)
    df['FWI'] = df['ISI'] * 1.5  # Simplificação para o protótipo
    
    return df