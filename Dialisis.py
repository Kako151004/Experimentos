import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import linregress
import streamlit as st



# STREAMLIT
st.set_page_config(page_title="Dialisis")

st.title("Dialisis| Laboratorio numero 3")
st.write("Interactua con la barra lateral izquierda para modificar los datos")

if "HistorialCalibrado" not in st.session_state:
    st.session_state.HistorialCalibrado = []

if "HistorialDialisis" not in st.session_state:
    st.session_state.HistorialDialisis = []

if "ListaCondiciones" not in st.session_state:
    st.session_state.ListaCondiciones = [
        "20°C - 0rpm", "20°C - 100rpm", "20°C - 200rpm",
        "30°C - 0rpm", "30°C - 100rpm", "30°C - 200rpm",
        "40°C - 0rpm", "40°C - 100rpm", "40°C - 200rpm"
    ]

st.sidebar.header("Parametros y curva de calibrado")
tiempos_input = st.sidebar.text_input("Tiempos de muestreo (separados por espacios)(min): ", value = "0 5 10 15 20 30 45 60")
st.sidebar.markdown("---")
st.sidebar.subheader("Datos de Calibrado")
input_conc_e = st.sidebar.text_area("Concentración estándar (mg/mL)","0 1 2 3 4 5 6")
input_abs_e = st.sidebar.text_area("ABS estándar (600 nm)", "")

col_b1, col_b2 = st.sidebar.columns(2)
guardar_ABS_estandar = col_b1.button("Guardar Replica Estandar")
limpiar_historial1= col_b2.button("Limpiar todo")

if limpiar_historial1:
    st.session_state.HistorialCalibrado = []
    st.success("Historial reiniciado.")

if guardar_ABS_estandar:
    try:
        abs_e = np.array([float(x) for x in input_abs_e.split()])
        conc_e = np.array([float(x) for x in input_conc_e.split()])
        if len(abs_e) != len(conc_e):
            st.error("La cantidad de valores en Concentraciónes y ABS deben ser iguales")
        else:
            st.session_state.HistorialCalibrado.append({"ConcE":conc_e, "ABSE":abs_e })
            st.success(f"Replica #{len(st.session_state.HistorialCalibrado)} guardada con exito")
    except ValueError:
        st.error("introduce los valores separados por espacios")

if len(st.session_state.HistorialCalibrado) >0:
    st.markdown("---")
    st.subheader("Resultados de calibrado")
    
    ConcentracionEM = np.array([item["ConcE"] for item in st.session_state.HistorialCalibrado])
    AbsEM = np.array([item["ABSE"] for item in st.session_state.HistorialCalibrado])
    ConcC = ConcentracionEM[-1]
    PromedioABSE = np.mean(AbsEM, axis = 0)
    
    st.write(f"**Número de réplicas acumuladas:** {len(st.session_state.HistorialCalibrado)}")
    st.write("**Promedio de Absorbancias:**", PromedioABSE)
    
    m, b, r ,_ ,_ = linregress(ConcC, PromedioABSE)
    R2 = r**2
    Ecuación = f"A = {m:.4f}*C+{b:.4f}  |   R2 = {R2:.4f}"
    
    st.session_state.HistorialDialisis.append({"PromedioAbsE": PromedioABSE, "pendiente": m, "intercepto": b})
    
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.plot(ConcC, PromedioABSE, marker='o', color='green', label=Ecuación)
    ax.set_title("Curva de calibrado")
    ax.set_xlabel('Concentración (mg/mL)')
    ax.set_ylabel('Absorbancia 600')
    ax.grid(True)
    ax.legend()
    
    # Mostrar el gráfico en Streamlit
    st.pyplot(fig)
    
