import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import linregress
import streamlit as st
import pandas as pd



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
Volumen_agua = st.sidebar.number_input("Volumen agua (mL)", value = 1.00, format = "%.5f")
tiempos_input = st.sidebar.text_input("Tiempos de muestreo (separados por espacios)(min): ", value = "0 5 10 15 20 30 45 60")
tiempos_muestreo = np.array([float(x) for x in tiempos_input.split()])
st.sidebar.markdown("---")
st.sidebar.subheader("Datos de Calibrado")
input_conc_e = st.sidebar.text_area("Concentración estándar (mg/mL)","0 1 2 3 4 5 6")
input_abs_e = st.sidebar.text_area("ABS estándar (600 nm)", "0.017 0.11 0.201 0.291 0.389 0.477 0.568")

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
if len(st.session_state.HistorialCalibrado) > 0:
    st.markdown("---")
    st.subheader("Resultados de calibrado")
    
    try:
        # Extraemos de forma segura
        ConcentracionEM = [item["ConcE"] for item in st.session_state.HistorialCalibrado]
        AbsEM = [item["ABSE"] for item in st.session_state.HistorialCalibrado]
        
        # Tomamos la última concentración introducida
        ConcC = ConcentracionEM[-1]
        
        # Validamos que todas las réplicas tengan la misma cantidad de puntos
        abs_matriz = np.array(AbsEM)
        
        # Promedio y Desviación Estándar
        PromedioABSE = np.mean(abs_matriz, axis=0)
        DesviacionABSE = np.std(abs_matriz, axis=0, ddof=1) if len(AbsEM) > 1 else np.zeros_like(PromedioABSE)
        
        st.write(f"**Número de réplicas acumuladas:** {len(st.session_state.HistorialCalibrado)}")
        
        # 📌 Unir promedio y desviación estándar
        abs_con_sd = [
            f"{p:.4f} ± {s:.4f}" if len(AbsEM) > 1 else f"{p:.4f} (n=1)"
            for p, s in zip(PromedioABSE, DesviacionABSE)
        ]
        
        df_calibracion = pd.DataFrame({
            "Concentración (mg/mL)": ConcC,
            "Absorbancia (Promedio ± SD)": abs_con_sd
        })
        st.dataframe(df_calibracion, use_container_width=True)
        
        # Regresión lineal
        m, b, r, _, _ = linregress(ConcC, PromedioABSE)
        R2 = r**2
        Ecuación = f"A = {m:.4f}*C + {b:.4f}  |  R² = {R2:.4f}"
        
        st.session_state.Pendiente = m
        st.session_state.Intercepto = b
        
        # Gráfico
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.errorbar(ConcC, PromedioABSE, yerr=DesviacionABSE, fmt='o', color='green', ecolor='gray', capsize=4, label=Ecuación)
        ax.set_title("Curva de calibrado")
        ax.set_xlabel('Concentración (mg/mL)')
        ax.set_ylabel('Absorbancia 600')
        ax.grid(True)
        ax.legend()
        
        st.pyplot(fig)
        
    except ValueError:
        st.error("Error: Asegúrate de que todas las réplicas tengan exactamente el mismo número de valores de absorbancia y concentración. Pulsa 'Limpiar todo' si necesitas reiniciar los datos.")

st.sidebar.header("Datos experimentales")
tipo_ingreso = st.sidebar.radio("Modo de condición", ["Elegir existente", "Crear nueva condición"])

if tipo_ingreso == "Elegir existente":
    condicion_base = st.sidebar.selectbox("Selecciona la condición base", st.session_state.ListaCondiciones)
    condicion_nombre = condicion_base
else:
    Temperatura_nueva = st.sidebar.text_input("Nombre de la temperatura","50°C")
    Agitacion_nueva = st.sidebar.text_input("Nombre de la agitación", "300rpm")
    condicion_nombre = f"{Temperatura_nueva.strip()} - {Agitacion_nueva}"
    
    if condicion_nombre and condicion_nombre not in st.session_state.ListaCondiciones:
        st.session_state.ListaCondiciones.append(condicion_nombre)

input_abs_exp = st.sidebar.text_area("ABS experimental (600 nm) (separados por espacios)", " 0.024 0.064 0.102 0.14 0.158 0.222 0.294 0.345")

col_exp1, col_exp2 = st.sidebar.columns(2)
guardar_corrida1 = col_exp1.button("Guardar Replica")
limpiar_historial2 = col_exp2.button("Limpiar todo")

if limpiar_historial2:
    st.session_state.HistorialDialisis = []
    st.success("Historial reiniciado.")

if guardar_corrida1:
    try:
        abs_exp = np.array([float(x) for x in input_abs_exp.split()])
        
        if len(abs_exp) != len(tiempos_muestreo):
            st.sidebar.error("La cantidad de valores de ABS deben ser iguales a las del Tiempo")
        else:
            concentracion = (abs_exp-b)/m
            masa_aparente = concentracion * Volumen_agua
            c_ultimo = concentracion[-1] if len(concentracion) > 0 and concentracion[-1] > 0 else 1.0
            fraccion_relativa = ((concentracion-concentracion[0])/(c_ultimo-concentracion[0]))*100
            grupo_base = condicion_nombre.strip()
            replicas_existentes = [item for item in st.session_state.HistorialDialisis if item["Grupo"]==grupo_base]
            num_replica = len(replicas_existentes)+1
            st.session_state.HistorialDialisis.append({
                "Grupo": grupo_base, "ID_Replica": num_replica, "EtiquetaCompleta": f"{grupo_base} (R{num_replica})", 
                "ABSExperimental": abs_exp, "Concentracion": concentracion, "MasaAparente": masa_aparente,
                "FraccionRelativa": fraccion_relativa
            })
            st.sidebar.success(f"Guardado: {grupo_base} (Réplica #{num_replica})")
    
    except Exception as e:
        st.sidebar.error(f"Error procesando datos: {e}")
        
