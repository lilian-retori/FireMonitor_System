import geopandas as gpd
import pandas as pd
from shapely.geometry import Point

def check_fire_risk_zones(df):
    """
    Converte coordenadas em pontos geométricos e define risco.
    """
    # Converter DataFrame comum para GeoDataFrame
    geometry = [Point(xy) for xy in zip(df.longitude, df.latitude)]
    gdf = gpd.GeoDataFrame(df, geometry=geometry)
    
    # Lógica de Risco: Se FWI > 10, Risco é Alto
    def classificar_risco(valor_fwi):
        if valor_fwi > 50: return 'CRÍTICO'
        if valor_fwi > 20: return 'ALTO'
        return 'MODERADO'
    
    gdf['nivel_risco'] = gdf['FWI'].apply(classificar_risco)
    
    return gdf