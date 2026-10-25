import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import linregress
import streamlit as st
import pandas as pd

# Encabezado
st.set_page_config(page_title="Taller 1| Laboratorio de fermentaciones")
st.title("Crecimiento microbiano| Del dato bruto a la cinética microbiana")
st.write("Temas: Biomasa seca/ OD_600 / Glucosa / Crecimiento y consumo")

# Historiales
if "HistorialdeCalibrado" not in st.session_state:
    st.session_state.HistorialdeCalibrado = []
    
if "HistorialdeCalculos" not in st.session_state:
    st.session_state.HistorialdeCalculos = []

if "ListadeReactores" not in st.session_state:
    st.session_state.ListadeReactores = ["Bioreactor 1", "Bioreactor 2", "Bioreactor 3"]

if "AnalisisBlancos" not in st.session_state:
    st.session_state.AnalisisBlancos = []
    
if "ListadeCondicionMS" not in st.session_state:
    st.session_state.ListadeCondicionMS = ["Suspensión 1", "Suspensión 2", "Suspensión 3", "Suspensión 4", "Suspensión 5", "Suspensión 6", "Suspensión 7", "Suspensión 8", "Suspensión 9"]
    
if "HistorialdeBiomasaSeca" not in st.session_state:
    st.session_state.HistorialdeBiomasaSeca = []
if "HistorialdeCineticaCultivo" not in st.session_state:
    st.session_state.HistorialdeCineticaCultivo = []
    
if "HistorialdeBiomasaSecaCinetico" not in st.session_state:
    st.session_state.HistorialdeBiomasaSecaCinetico = []
# Barra lateral

st.sidebar.header("Analisis de los blancos independientes")
input_Abs600BI = st.sidebar.text_input("Absorbancias (600 nm)", " 0.024 0.032 0.033 0.027 0.029")
input_Abs505BI = st.sidebar.text_input("Absorbancias (505 nm)", " 0.024 0.032 0.033 0.027 0.029")
col_b1, col_b2 = st.sidebar.columns(2)
Guardar_analisis = col_b1.button("Guardar analisis")
Borrar_analisis = col_b2.button("Borrar analisis")
if Borrar_analisis:
    st.session_state.AnalisisBlancos = []
    st.sidebar.success("Analisis borrado")
if Guardar_analisis:
    Abs600BI = np.array([float(x) for x in input_Abs600BI.split()])
    Abs505BI = np.array([float(x) for x in input_Abs505BI.split()])
    st.session_state.AnalisisBlancos.append({"ABS600BI": Abs600BI,"ABS505BI": Abs505BI})
    st.sidebar.success("Analisis guardado")
st.sidebar.markdown("---")

st.sidebar.header("Curva de calibración de la glucosa (ABS505)")
input_Abs505CA = st.sidebar.text_input("Absorbancias (505 nm)", " 0.031 0.102 0.186 0.298 0.400 0.547 0.703 0.921")
input_ConcPatronCA = st.sidebar.text_input("Concentración patron (g/L)", " 0.0 0.1 0.2 0.35 0.5 0.7 0.9 1.2")
col_b1, col_b2 = st.sidebar.columns(2)
Guardar_analisis1 = col_b1.button("Guardar Calibrado")
Borrar_analisis1 = col_b2.button("Borrar Calibrado")
if Borrar_analisis1:
    st.session_state.HistorialdeCalibrado = []
    st.sidebar.success("Calibrado borrado")
if Guardar_analisis1:
    try:
        Abs505CA = np.array([float(x) for x in input_Abs505CA.split()])
        ConcPatronCA = np.array([float(x) for x in input_ConcPatronCA.split()])
        if len(Abs505CA) != len(ConcPatronCA):
            st.error("La cantidad de valores en concentracion y abs deben ser la misma")
        else:
            st.session_state.HistorialdeCalibrado.append({"ABS505Ca": Abs505CA,"ConcPatronCa": ConcPatronCA})
            st.sidebar.success(f"Replica # {len(st.session_state.HistorialdeCalibrado)} guardado con exito")
    except ValueError:
        st.error("introduce los valores separados por espacios")
st.sidebar.markdown("---")

st.sidebar.header("Calibración de biomasa seca frente a OD600")
condicion_base = st.sidebar.selectbox("Selecciona la condición base", st.session_state.ListadeCondicionMS)
condicion_nombre = condicion_base
Volumen = st.sidebar.number_input("Volumen centrifugado (mL)", value = 50.00, format = "%.4f")
MasaR = st.sidebar.number_input("Masa de Recipiente seco (g)", value = 16.8690, format = "%.4f")
MasaRC = st.sidebar.number_input("Masa de recipiente seco + celulas (g)", value = 16.8736, format = "%.4f")
DilucionMC = st.sidebar.number_input("Dilución OD (1:x)", value = 1, format = "%.2f")
OD600Mc = st.sidebar.number_input("OD 600", value = 0.248, format = "%.3f")
col_b1, col_b2 = st.sidebar.columns(2)
Guardar_analisis2 = col_b1.button("Guardar Registro")
Borrar_analisis2 = col_b2.button("Borrar Registro")
if Borrar_analisis2:
    st.session_state.HistorialdeBiomasaSeca = []
    st.sidebar.success("Calibrado borrado")
if Guardar_analisis2:
    grupo_base = condicion_nombre.strip()
    replicas_existentes = [item for item in st.session_state.HistorialdeBiomasaSeca if item["Grupo"]==grupo_base]
    num_replica = len(replicas_existentes)+1
    st.session_state.HistorialdeBiomasaSeca.append({
        "Grupo": grupo_base, "ID_Replica": num_replica, "Etiqueta completa": f"{grupo_base} (R{num_replica})",
        "VolumenC": Volumen, "MasaR": MasaR, "MasaR+C": MasaRC, "DilucionMC": DilucionMC, "Abs600MC": OD600Mc
    })
    st.sidebar.success(f"Guardado: {grupo_base} (Réplica #{num_replica})")
st.sidebar.markdown("---")

st.sidebar.header("Cinetica de cultivo")
condicion_base2 = st.sidebar.selectbox("Selecciona la condición base", st.session_state.ListadeReactores)
condicion_nombre2 = condicion_base2
input_tiempoCC = st.sidebar.text_area("Tiempo (h)", "0 1 2 3 4 5 6 7 8 9 10 11 12")
input_Dilucion600CC = st.sidebar.text_area("Dilución  OD (1:x)", "1 1 1 1 2 2 3 5 6 8 9 10 10")
input_Abs600CC = st.sidebar.text_area("OD 600", "0.224 0.300 0.421 0.583 0.451 0.675 0.667 0.591 0.690 0.672 0.705 0.694 0.699 ")
input_Dilucion505CC = st.sidebar.text_area("Dilucion glucosa", "10 10 10 10 10 10 10 5 5 5 5 2 2")
input_Abs505CC = st.sidebar.text_area("Abs 505","0.514 0.512 0.513 0.487 0.479 0.447 0.423 0.677 0.558 0.410 0.284 0.436 0.357")
col_b1, col_b2 = st.sidebar.columns(2)
Guardar_analisis3 =col_b1.button("Guardar Replicas")
Borrar_analisis3 = col_b2.button("Limpiar Replicas")

if Borrar_analisis3:
    st.session_state.HistorialdeCineticaCultivo = []
    st.sidebar.success("Historial reiniciado")
if Guardar_analisis3:
    try:
        tiempoCC = np.array([float(x) for x in input_tiempoCC.split()])
        Dilucion600CC = np.array([float(x) for x in input_Dilucion600CC.split()])
        Abs600CC = np.array([float(x) for x in input_Abs600CC.split()])
        Dilucion505CC = np.array([float(x) for x in input_Dilucion505CC.split()])
        Abs505CC = np.array([float(x) for x in input_Abs505CC.split()])
        if len(tiempoCC) != len(Dilucion600CC) != len(Abs600CC) != len(Dilucion505CC) != len(Abs505CC):
            st.error("La cantidad de valores debe ser igual para todos los paremetros en esta seccion")
        else:
            grupo_base2 = condicion_nombre2.strip()
            replicas_existentes2 = [item for item in st.session_state.HistorialdeCineticaCultivo if item["Grupo"]==grupo_base2]
            num_replica2 = len(replicas_existentes2)+1
            st.session_state.HistorialdeCineticaCultivo.append({
                "TiempoCC": tiempoCC, "Dilucion600CC": Dilucion600CC, "Abs600CC": Abs600CC, "Dilucion505CC": Dilucion505CC, "Abs505CC": Abs505CC,
                "Grupo": grupo_base2, "ID_Replica": num_replica2, "Etiqueta completa": f"{grupo_base2} (R{num_replica2})"})
            st.sidebar.success(f"Guardado: {grupo_base2} (Réplica #{num_replica2})")
    except Exception as e:
        st.sidebar.error(f"Error procesando datos: {e}")
st.sidebar.markdown("---")

st.sidebar.header("Biomasa durante el cultivo")
condicion_base3 = st.sidebar.selectbox("Selecciona el reactor", st.session_state.ListadeReactores)
condicion_nombre3 = condicion_base3
input_tiempoMSC = st.sidebar.text_area("Tiempo (h)", "0 3 6 9 12")
Volumen1 = st.sidebar.number_input("Volumen centrifugado parte 4 (mL)", value = 50.00, format = "%.4f")
input_MasaS_MSC = st.sidebar.text_area("Masa seca (g) parte 4", "15.2403 15.3232 14.4242 14.2118 14.1435")
input_MasaSC_MSC = st.sidebar.text_area("Masa seca + celulas (g) parte 4", "15.2403 15.3232 14.4242 14.2118 14.1435")
col_b1, col_b2 = st.sidebar.columns(2)
Guardar_analisis4 =col_b1.button("Almacenar Replicas")
Borrar_analisis4 = col_b2.button("Eliminar Replicas")

if Borrar_analisis4:
    st.session_state.HistorialdeBiomasaSecaCinetico = []
    st.sidebar.success("Historial reiniciado")
if Guardar_analisis4:
    try:
        tiempoMSC = np.array([float(x) for x in input_tiempoMSC.split()])
        MasaS_MSC = np.array([float(x) for x in input_MasaS_MSC.split()])
        MasaSC_MSC = np.array([float(x) for x in input_MasaSC_MSC.split()])
        Abs505CC = np.array([float(x) for x in input_Abs505CC.split()])
        if len(tiempoMSC) != len(MasaS_MSC) != len(MasaSC_MSC):
            st.error("La cantidad de valores debe ser igual para todos los paremetros en esta seccion")
        else:
            grupo_base3 = condicion_nombre3.strip()
            replicas_existentes3 = [item for item in st.session_state.HistorialdeBiomasaSecaCinetico if item["Grupo"]==grupo_base3]
            num_replica3 = len(replicas_existentes3)+1
            st.session_state.HistorialdeBiomasaSecaCinetico.append({
                "TiempoMSC": tiempoMSC, "MasaS_MSC": MasaS_MSC, "MasaSC_MSC": MasaSC_MSC,
                "Grupo": grupo_base3, "ID_Replica": num_replica3, "Etiqueta completa": f"{grupo_base3} (R{num_replica3})"})
            st.sidebar.success(f"Guardado: {grupo_base3} (Réplica #{num_replica3})")
    except Exception as e:
        st.sidebar.error(f"Error procesando datos: {e}")
