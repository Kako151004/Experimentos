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
# Barra lateral
st.sidebar.header("Parametros")
st.sidebar.markdown("---")

st.sidebar.header("Analisis de los blancos independientes")
input_Abs600BI = st.sidebar.text_input("Absorbancias (600 nm)", " 0.024 0.032 0.033 0.027 0.029")
input_Abs505BI = st.sidebar.text_input("Absorbancias (505 nm)", " 0.024 0.032 0.033 0.027 0.029")
col_b1, col_b2 = st.sidebar.columns(2)
Guardar_analisis = col_b1.button("Guardar analisis")
Borrar_analisis = col_b2.button("Borrar analisis")
if Borrar_analisis:
    st.session_state.AnalisisBlancos = []
    st.success("Analisis borrado")
if Guardar_analisis:
    Abs600BI = np.array([float(x) for x in input_Abs600BI.split()])
    Abs505BI = np.array([float(x) for x in input_Abs505BI.split()])
    st.session_state.AnalisisBlancos.append({"ABS600BI": Abs600BI,"ABS505BI": Abs505BI})
    st.success("Analisis guardado")
st.sidebar.markdown("---")

st.sidebar.header("Curva de calibración de la glucosa (ABS505)")
input_Abs505CA = st.sidebar.text_input("Absorbancias (505 nm)", " 0.031 0.102 0.186 0.298 0.400 0.547 0.703 0.921")
input_ConcPatronCA = st.sidebar.text_input("Absorbancias (g/L)", " 0.0 0.1 0.2 0.35 0.5 0.7 0.9 1.2")
col_b1, col_b2 = st.sidebar.columns(2)
Guardar_analisis1 = col_b1.button("Guardar Calibrado")
Borrar_analisis1 = col_b2.button("Borrar Calibrado")
if Borrar_analisis1:
    st.session_state.HistorialdeCalibrado = []
    st.success("Calibrado borrado")
if Guardar_analisis1:
    try:
        Abs505CA = np.array([float(x) for x in input_Abs505CA.split()])
        ConcPatronCA = np.array([float(x) for x in input_ConcPatronCA.split()])
        if len(Abs505CA) != len(ConcPatronCA):
            st.error("La cantidad de valores en concentracion y abs deben ser la misma")
        else:
            st.session_state.HistorialdeCalibrado.append({"ABS505Ca": Abs505CA,"ConcPatronCa": ConcPatronCA})
            st.success(f"Replica # {len(st.session_state.HistorialdeCalibrado)} guardado con exito")
    except ValueError:
        st.error("introduce los valores separados por espacios")
st.sidebar.markdown("---")

st.sidebar.header("Calibración de biomasa seca frente a OD600")
st.sidebar.markdown("---")

st.sidebar.header("Cinetica de cultivo")
st.sidebar.markdown("---")

st.sidebar.header("Biomasa durante el cultivo")

