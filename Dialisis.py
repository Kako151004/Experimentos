import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Configuración de la página para identificarla fácilmente en el teléfono
st.set_page_config(
    page_title="Lab Diálisis",
    page_icon="🧬",
    layout="centered"
)

st.title("🧪 Análisis de Datos: Laboratorio de Diálisis")
st.markdown("Esta aplicación permite procesar los datos experimentales de difusión y separación por membrana.")

# Sección para ingresar o cargar datos
st.subheader("1. Registro de Concentración vs. Tiempo")

# Ejemplo de entrada de datos simulados o manuales
tiempo = st.slider("Selecciona el tiempo de muestreo (minutos)", 0, 120, 10)
concentracion_externa = st.number_input("Concentración en el dializado (g/L)", value=0.0)

# Aquí puedes integrar la lógica para calcular coeficientes o graficar
st.write(f"Registrando datos para t = {tiempo} min con una concentración de {concentracion_externa} g/L.")

# Gráfico de ejemplo (puedes adaptarlo con tus datos reales de Pandas)
if st.button("Generar gráfico de difusión"):
    datos_ejemplo = pd.DataFrame({
        'Tiempo': [0, 30, 60, 90, 120],
        'Concentracion': [0.0, 1.2, 2.3, 3.0, 3.5]
    })
    
    fig, ax = plt.subplots()
    ax.plot(datos_ejemplo['Tiempo'], datos_ejemplo['Concentracion'], marker='o', color='purple')
    ax.set_xlabel("Tiempo (min)")
    ax.set_ylabel("Concentración (g/L)")
    ax.set_title("Cinética de Diálisis")
    
    st.pyplot(fig)
