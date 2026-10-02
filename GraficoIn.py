import streamlit as st
import pandas as pd
import numpy as np

# Configuración de la página en modo ancho
st.set_page_config(layout="wide", page_title="Simulador Climático Interactivo")

st.title("🌍 Simulador Interactivo: Temperatura Global y el Ártico")
st.markdown("**Instrucciones para la presentación:** Mueve la barra deslizante inferior para viajar en el tiempo desde la era preindustrial hasta las proyecciones futuras.")

st.divider()

# Barra deslizante interactiva para elegir el año
year = st.slider("Selecciona el Año de Análisis:", min_value=1850, max_value=2060, value=2024, step=2)

# Lógica de datos según el año seleccionado
if year <= 1900:
    temp = 0.0
    co2 = 280
    status = "Etapa Preindustrial (Equilibrio natural)"
    desc = "Concentración estable de CO2. Los casquetes polares y el hielo marino se encuentran en su máxima estabilidad histórica."
    # Puntos densos simulando hielo completo en el mapa
    map_data = pd.DataFrame({'lat': np.random.uniform(75, 85, 100), 'lon': np.random.uniform(-180, 180, 100)})

elif year <= 1980:
    temp = round((year - 1900) * 0.004 + 0.1, 2)
    co2 = int(280 + (year - 1950) * 0.7 if year >= 1950 else 280)
    status = "Aceleración Industrial Temprana"
    desc = "Comienza el aumento sostenido de emisiones por quema masiva de combustibles fósiles."
    map_data = pd.DataFrame({'lat': np.random.uniform(73, 85, 70), 'lon': np.random.uniform(-180, 180, 70)})

elif year <= 2026:
    temp = round(1.2 + (year - 2020) * 0.06, 2)
    co2 = int(415 + (year - 2020) * 3)
    status = "⚠️ Actualidad (Récords de Calentamiento)"
    desc = "Superamos los +1.5°C en años recientes (2024-2025). El Ártico sufre un calentamiento asimétrico (2 a 3 veces más rápido)."
    map_data = pd.DataFrame({'lat': np.random.uniform(70, 85, 35), 'lon': np.random.uniform(-180, 180, 35)})

else:
    temp = round(1.6 + (year - 2026) * 0.025, 2)
    co2 = int(430 + (year - 2026) * 2.5)
    status = "🚨 Futuro Crítico / Zona de Puntos de Inflexión"
    desc = "Rumbo a los 550 ppm. Alto riesgo de veranos libres de hielo en el Ártico y desestabilización de corrientes marinas."
    map_data = pd.DataFrame({'lat': np.random.uniform(68, 82, 15), 'lon': np.random.uniform(-180, 180, 15)})

# Estructura en dos columnas (Izquierda: Datos | Derecha: Mapa)
col1, col2 = st.columns(2, gap="large")

with col1:
    st.subheader(f"📊 Año analizado: {year}")
    
    # Métricas cuantitativas visuales
    st.metric(label="Aumento de Temperatura Media Global", value=f"+{temp} °C", delta="Respecto a 1850-1900")
    st.metric(label="Concentración Atmosférica de CO₂", value=f"{co2} ppm", delta=f"+{co2 - 280} ppm sobre nivel natural")
    
    st.markdown("### Estado del Sistema Climático:")
    st.info(f"**{status}**")
    st.write(desc)

with col2:
    st.subheader("🗺️ Vista Satelital: Retracción del Hielo Ártico")
    st.markdown("Cada punto representa la presencia de capas de hielo estables. Nota cómo disminuyen con el tiempo:")
    
    # Mapa interactivo centrado en el Ártico
    st.map(map_data, latitude=80.0, longitude=0.0, zoom=1.5)
    st.caption("Simulación basada en la reducción de la extensión del hielo marino polar.")

st.divider()
st.markdown("*Herramienta desarrollada para presentación académica de Biotecnología / Cambio Climático.*")