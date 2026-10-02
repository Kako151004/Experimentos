import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# ==========================================
# 1. CONFIGURACIÓN DE LA PÁGINA (Para el teléfono)
# ==========================================
st.set_page_config(
    page_title="Lab Diálisis",  # Cambiar según el laboratorio (ej. "Lab Liofilización")
    page_icon="🧬",             # Emoji representativo
    layout="centered"
)

st.title("🧪 Laboratorio de Separación por Membrana (Diálisis)")
st.markdown("Herramienta de cálculo y análisis de datos experimentales.")

# ==========================================
# 2. ENTRADA DE DATOS (Sidebar o Formulario Principal)
# ==========================================
st.sidebar.header("Parámetros Operativos")

# Ejemplo de entradas de datos
volumen_muestra = st.sidebar.number_input("Volumen de la solución (mL)", value=100.0)
tiempo_total = st.sidebar.slider("Tiempo total de ensayo (min)", 0, 180, 60, step=10)

st.subheader("📊 Ingreso de Puntos Experimentales")
st.markdown("Ingrese los valores medidos durante la práctica:")

# Simulación de tabla editable o entradas dinámicas
# (Aquí puedes ajustar según las columnas de tu reporte)
num_puntos = st.sidebar.number_input("Número de muestras tomadas", min_value=3, max_value=10, value=5)

tiempos = []
concentraciones = []

for i in range(int(num_puntos)):
    col1, col2 = st.columns(2)
    with col1:
        t = st.number_input(f"Tiempo t_{i} (min)", value=float(i * 15), key=f"t_{i}")
        tiempos.append(t)
    with col2:
        c = st.number_input(f"Conc. C_{i} (g/L)", value=float(10.0 / (i + 1)), key=f"c_{i}")
        concentraciones.append(c)

# Crear DataFrame con los datos ingresados
df_datos = pd.DataFrame({
    'Tiempo (min)': tiempos,
    'Concentración (g/L)': concentraciones
})

# ==========================================
# 3. CÁLCULOS Y RESULTADOS
# ==========================================
st.subheader("📈 Resultados y Gráficos")

if st.button("Procesar y Graficar Datos"):
    # Mostrar tabla resumen
    st.dataframe(df_datos)
    
    # Generar gráfico de comportamiento
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.plot(df_datos['Tiempo (min)'], df_datos['Concentración (g/L)'], marker='o', linestyle='-', color='teal', linewidth=2)
    ax.set_xlabel("Tiempo (min)")
    ax.set_ylabel("Concentración (g/L)")
    ax.set_title("Cinética del Proceso")
    ax.grid(True, linestyle='--', alpha=0.6)
    
    st.pyplot(fig)
    
    st.success("¡Datos procesados exitosamente!")
