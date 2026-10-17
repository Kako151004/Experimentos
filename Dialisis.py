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

col_exp1, col_exp2= st.sidebar.columns(2)
guardar_corrida1 = col_exp1.button("Guardar Replica")
limpiar_historial2 = col_exp2.button("Limpiar Dialisis")

if limpiar_historial2:
    st.session_state.HistorialDialisis = []
    st.success("Historial reiniciado.")

if guardar_corrida1:
    try:
        abs_exp = np.array([float(x) for x in input_abs_exp.split()])
        
        if len(abs_exp) != len(tiempos_muestreo):
            st.sidebar.error("La cantidad de valores de ABS deben ser iguales a las del Tiempo")
        else:
            m_cal = st.session_state.Pendiente
            b_cal = st.session_state.Intercepto
            
            concentracion = (abs_exp-b_cal)/m_cal
            masa_aparente = concentracion * Volumen_agua
            c_ultimo = concentracion[-1] if len(concentracion) > 0 and concentracion[-1] > 0 else 1.0
            fraccion_relativa = ((concentracion)/(c_ultimo))*100
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

historial = st.session_state.HistorialDialisis
if len(historial)>0:
    st.markdown('---')
    st.subheader(f"Panel de resultados y control ({len(historial)}) registros totales")
    
    grupos_unicos = sorted(list(set(item["Grupo"] for item in historial)))
    Temperatura_base = sorted(list(set([g.split(" - ")[0] for g in grupos_unicos if " - " in g])))
    
    datos_agrupados = {}
    for grupo in grupos_unicos:
        corridas_grupo = [item for item in historial if item["Grupo"] == grupo]
        MatrizABS = np.array([c["ABSExperimental"] for c in corridas_grupo])
        MatrizConc = np.array([c["Concentracion"] for c in corridas_grupo])
        MatrizMasa = np.array([c["MasaAparente"] for c in corridas_grupo])
        MatrizFrac = np.array([c["FraccionRelativa"] for c in corridas_grupo])
        
        PromABS = np.mean(MatrizABS, axis = 0)
        StdABS = np.std(MatrizABS, axis = 0, ddof = 1) if len(corridas_grupo) > 1 else np.zeros_like(PromABS)
        PromConc = np.mean(MatrizConc, axis = 0)
        StdConc = np.std(MatrizConc, axis = 0, ddof = 1) if len(corridas_grupo) >1 else np.zeros_like(PromConc)
        PromMasa = np.mean(MatrizMasa, axis = 0)
        PromFrac = np.mean(MatrizFrac, axis = 0)
        tm = np.diff(tiempos_muestreo)
        DifConc = np.diff(PromConc)
        Velocidad_promedio_grupo = DifConc/ tm if np.all(tm>0) else np.zeros_like(DifConc)
        datos_agrupados[grupo] = { "Tiempos" : tiempos_muestreo, "AbsProm": PromABS, "AbsStd":StdABS,
                                  "ConcProm": PromConc, "ConcStd": StdConc, "MasaProm": PromMasa, "FracProm": PromFrac,
                                  "VelocidadPromedio" : Velocidad_promedio_grupo, "Corridas":corridas_grupo}
        
    tabs = st.tabs([f"{g}" for g in grupos_unicos]+["Global", "Agitación y resistencia externa", "Temperatura y Arrhenius", "Cinetica y tiempos de proceso", "Optimización y escalamiento", "ANOVA"])
    for idx, grupo in enumerate(grupos_unicos):
        d = datos_agrupados[grupo]
        with tabs[idx]:
            st.write(f"### Condición: **{grupo}** ({len(d["Corridas"])} réplica(s) agrupadas)")
            st.write("### Resumen Estadístico")
            tabla_resumen = {
                "Tiempo (min)": [int(t) for t in tiempos_muestreo],
                "ABS Prom +- SD": [f"{d["AbsProm"][i]:.3f}+-{d["AbsStd"][i]:.3f}" for i in range(len(tiempos_muestreo))],
                "Conc. Prom +- SD (mg/mL)": [f"{d["ConcProm"][i]:.3f}+-{d["ConcStd"][i]:.3f}" for i in range(len(tiempos_muestreo))],
                "Masa Soluto Extractor(mg)": [f"{v:.2f}" for v in d["MasaProm"]],
                "Fracción relativa (%)":  [f"{v:.2f}%" for v in d["FracProm"]]
            }
            st.dataframe(tabla_resumen, use_container_width=True)
            st.write("##### Velocidad Promedio de Extracción por Intervalos")
            if len(tiempos_muestreo) >1:
                tabla_2_datos = {
                    "Intervalo de tiempo (min)": [f"{int(ti)} a {int(tf)}" for ti, tf in zip(tiempos_muestreo[:-1], tiempos_muestreo[1:])],
                    "Velocidad promedio ((mg/ml)/min)": [f"{vm:.4f}" for vm in d["VelocidadPromedio"]]
                }
                st.dataframe(tabla_2_datos, use_container_width = True)
            fig_g, ax_g = plt.subplots(figsize=(7,4))
            for c_item in d["Corridas"]:
                ax_g.plot(tiempos_muestreo, c_item["ConcProm"], linestyle = "--", alpha=0.4, label=f"R{c_item["ID_Replica"]}")
            ax_g.errorbar(tiempos_muestreo, d["ConcProm"], yerr = d["ConcStd"], fmt ="o-", color="black", linewidth=2, capsize=4,label="Promedio +- SD")
            ax_g.set_xlabel("Tiempo (min)")
            ax_g.set_ylabel("Concentracion (mg/mL)")
            ax_g.set_title(f"Cinética con Réplicas: {grupo}")
            ax_g.grid(True)
            ax_g.legend()
            st.pyplot(fig_g)
                
    
        
    
