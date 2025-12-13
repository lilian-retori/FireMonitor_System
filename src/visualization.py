import folium
from folium.plugins import HeatMap
from .config import MAPS_DIR
import os

def generate_risk_map(gdf):
    """
    Cria um mapa HTML com os focos.
    """
    # Centro do mapa (Média das coordenadas)
    center_lat = gdf['latitude'].mean()
    center_lon = gdf['longitude'].mean()
    
    m = folium.Map(location=[center_lat, center_lon], zoom_start=6)
    
    # Cores por risco
    colors = {'CRÍTICO': 'red', 'ALTO': 'orange', 'MODERADO': 'yellow'}
    
    for _, row in gdf.iterrows():
        folium.CircleMarker(
            location=[row['latitude'], row['longitude']],
            radius=5,
            color=colors.get(row['nivel_risco'], 'blue'),
            fill=True,
            popup=f"Risco: {row['nivel_risco']} (FWI: {row['FWI']:.1f})"
        ).add_to(m)
    
    # Salvar
    output_file = os.path.join(MAPS_DIR, "mapa_risco.html")
    m.save(output_file)
    return output_file