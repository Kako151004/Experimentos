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
ConcRef = st.sidebar.number_input("ConcentraciónReferencia (mg/mL)", value = 5.20, format = "%.5f")
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
        ax.plot(ConcC, PromedioABSE, linestyle = "--", color='green')
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
        Velocidad_promedio_0_10 = (PromConc[2]-PromConc[0])/(tiempos_muestreo[2]-tiempos_muestreo[0])
        
        valores_validos = PromConc < ConcRef
        if np.any(valores_validos):
            t_validos = tiempos_muestreo[valores_validos]
            c_validos = PromConc[valores_validos]
            dif_log = np.log(ConcRef-c_validos)
            m_k, b_k, r_k,_,_ = linregress(t_validos, dif_log)
            kapp = -m_k
            R2k = r_k**2
        else:
            kapp= 0.0
            R2K = 0.0
        
        if kapp > 0:
            import numpy as np
            t_50 = np.log(2) / kapp
            t_80 = np.log(5) / kapp
        else:
            t_50 = 0.0
            t_80 = 0.0
            
        
        
        
        datos_agrupados[grupo] = { "Tiempos" : tiempos_muestreo, "AbsProm": PromABS, "AbsStd":StdABS,
                                  "ConcProm": PromConc, "ConcStd": StdConc, "MasaProm": PromMasa, "FracProm": PromFrac,
                                  "VelocidadPromedio" : Velocidad_promedio_grupo, "Corridas":corridas_grupo,
                                  "VelocidadPromedio0-10":Velocidad_promedio_0_10, "Kapp": kapp, "RK": R2k,
                                  "t50": t_50, "t80": t_80}
        
    tabs = st.tabs([f"{g}" for g in grupos_unicos]+["Analisis del efecto de agitación y temperatura", "Modelación cinetica aparente y Arrhenius", "Interacción agitación x temperatura","Optimización y escalamiento"])
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
                ax_g.plot(tiempos_muestreo, c_item['Concentracion'], linestyle = "--", alpha=0.4, label=f"R{c_item["ID_Replica"]}")
            ax_g.errorbar(tiempos_muestreo, d["ConcProm"], yerr = d["ConcStd"], fmt ="o-", color="black", linewidth=2, capsize=4,label="Promedio +- SD")
            ax_g.set_xlabel("Tiempo (min)")
            ax_g.set_ylabel("Concentracion (mg/mL)")
            ax_g.set_title(f"Cinética con Réplicas: {grupo}")
            ax_g.grid(True)
            ax_g.legend()
            st.pyplot(fig_g)
    st.markdown("---")
    st.subheader("Panel de control de visualización")
    col_chk1, col_chk2 =st.columns(2)
    
    with col_chk1:
        st.markdown("##### Replicas individuales")
        corridas_seleccionadas= []
        for item in historial:
            if st.checkbox(item["EtiquetaCompleta"],value=False,key=f"chk_corrida_{item['EtiquetaCompleta']}"):
                corridas_seleccionadas.append(item)
    with col_chk2:
        st.markdown("##### Promedios de Grupos")
        grupos_seleccionados = []
        for grupo in grupos_unicos:
            if st.checkbox(f"Promedio: {grupo}",value=True, key=f"chk_grupo_{grupo}"):
                grupos_seleccionados.append(grupo)
    
    d= datos_agrupados[grupo]
    with tabs[len(grupos_unicos)]:
        st.subheader("Tabla de todos los Grupos")
        tabla_global = {"Tiempo (min)": [int(t) for t in tiempos_muestreo]}
        for grupo in grupos_unicos:
            tabla_global[f"{grupo} (Conc Prom +- SD)"] = [f"{datos_agrupados[grupo]['ConcProm'][i]:.3f} +- {datos_agrupados[grupo]['ConcStd'][i]:.3f}" for i in range(len(tiempos_muestreo))]
        st.dataframe(tabla_global, use_container_width = True)
        
        st.markdown("---")
        st.subheader("Ánalisis de la temperatura a base de la velocidad inicial (0-10 min)")
        
        incrementos_data1 = []
        # Identificamos las temperaturas únicas a partir de los nombres de los grupos
        rpm_unicas = sorted(list(set([g.split(" - ")[1] for g in grupos_unicos if " - " in g])))
        
        for rpm in rpm_unicas:
            # Buscamos los nombres exactos para cada nivel de RPM en esa temperatura
            g_20 = f"20°C - {rpm}"
            g_30 = f"30°C - {rpm}"
            g_40 = f"40°C - {rpm}"
            
            # Obtenemos las velocidades iniciales si existen en los datos agrupados
            v20 = datos_agrupados[g_20]["VelocidadPromedio0-10"] if g_20 in datos_agrupados else None
            v30 = datos_agrupados[g_30]["VelocidadPromedio0-10"] if g_30 in datos_agrupados else None
            v40 = datos_agrupados[g_40]["VelocidadPromedio0-10"] if g_40 in datos_agrupados else None
            
            # Calculamos los incrementos porcentuales de forma segura
            inc_20_30 = ((v30 - v20) / v20 * 100) if (v20 is not None and v30 is not None and v20 != 0) else 0.0
            inc_30_40 = ((v40 - v30) / v30 * 100) if (v30 is not None and v40 is not None and v30 != 0) else 0.0
            inc_20_40 = ((v40 - v20) / v20 * 100) if (v20 is not None and v40 is not None and v20 != 0) else 0.0
            incrementos_data1.append({
                "Temperatura": rpm,
                "v0 (20°C)": f"{v20:.4f}" if v20 is not None else "N/A",
                "v0 (30°C)": f"{v30:.4f}" if v30 is not None else "N/A",
                "v0 (40°C)": f"{v40:.4f}" if v40 is not None else "N/A",
                "Incremento 20 → 30 °C (%)": f"{inc_20_30:.2f}%" if v20 is not None and v30 is not None else "N/A",
                "Incremento 30 → 40 °C (%)": f"{inc_30_40:.2f}%" if v30 is not None and v40 is not None else "N/A",
                "Incremento 20 → 40 °C (%)": f"{inc_20_40:.2f}%" if v20 is not None and v40 is not None else "N/A"
            })
            
        df_incrementos1 = pd.DataFrame(incrementos_data1)
        st.dataframe(df_incrementos1, use_container_width=True)
        st.markdown("---")
        st.subheader("Ánalisis de la agitación a partir de la velocidad inicial (0-10 min)")
        
        incrementos_data = []
        # Identificamos las temperaturas únicas a partir de los nombres de los grupos
        temperaturas_unicas = sorted(list(set([g.split(" - ")[0] for g in grupos_unicos if " - " in g])))
        
        for temp in temperaturas_unicas:
            # Buscamos los nombres exactos para cada nivel de RPM en esa temperatura
            g_0 = f"{temp} - 0rpm"
            g_100 = f"{temp} - 100rpm"
            g_200 = f"{temp} - 200rpm"
            
            # Obtenemos las velocidades iniciales si existen en los datos agrupados
            v0 = datos_agrupados[g_0]["VelocidadPromedio0-10"] if g_0 in datos_agrupados else None
            v100 = datos_agrupados[g_100]["VelocidadPromedio0-10"] if g_100 in datos_agrupados else None
            v200 = datos_agrupados[g_200]["VelocidadPromedio0-10"] if g_200 in datos_agrupados else None
            
            # Calculamos los incrementos porcentuales de forma segura
            inc_0_100 = ((v100 - v0) / v0 * 100) if (v0 is not None and v100 is not None and v0 != 0) else 0.0
            inc_100_200 = ((v200 - v100) / v100 * 100) if (v100 is not None and v200 is not None and v100 != 0) else 0.0
            inc_0_200 = ((v200 - v0) / v0 * 100) if (v0 is not None and v200 is not None and v0 != 0) else 0.0
            incrementos_data.append({
                "Temperatura": temp,
                "v0 (0 rpm)": f"{v0:.4f}" if v0 is not None else "N/A",
                "v0 (100 rpm)": f"{v100:.4f}" if v100 is not None else "N/A",
                "v0 (200 rpm)": f"{v200:.4f}" if v200 is not None else "N/A",
                "Incremento 0 → 100 rpm (%)": f"{inc_0_100:.2f}%" if v0 is not None and v100 is not None else "N/A",
                "Incremento 100 → 200 rpm (%)": f"{inc_100_200:.2f}%" if v100 is not None and v200 is not None else "N/A",
                "Incremento 0 → 200 rpm (%)": f"{inc_0_200:.2f}%" if v0 is not None and v200 is not None else "N/A"
            })
            
        df_incrementos = pd.DataFrame(incrementos_data)
        st.dataframe(df_incrementos, use_container_width=True)
        st.markdown("---")
        st.subheader("Gráfica global comparativa")
        if len(grupos_seleccionados)>0 or len(corridas_seleccionadas)>0:
            fig_glob,ax_glob = plt.subplots(figsize=(9,5))
            for grupo in grupos_seleccionados:
                d=datos_agrupados[grupo]
                ax_glob.errorbar(d["Tiempos"],d["ConcProm"],yerr=d["ConcStd"],marker="o",capsize=4,linewidth=2,label=f"Promedio:{grupo}")
            for c_item in corridas_seleccionadas:
                ax_glob.plot(tiempos_muestreo,c_item["Concentracion"], linestyle=":", alpha=0.6, marker="x", label=f"Réplica: {c_item['EtiquetaCompleta']}")
            ax_glob.set_xlabel("Tiempo (min)")
            ax_glob.set_ylabel("Concentración (mg/mL)")
            ax_glob.set_title("Comparativa global")
            ax_glob.grid(True)
            ax_glob.legend(bbox_to_anchor=(1.05,1),loc='upper left')
            plt.tight_layout()
            st.pyplot(fig_glob)
        else:
            st.warning("Selecciona al menos un grupo o réplica en el panel superior.")
    # 1. Creamos la pestaña de Modelación Cinética (asumiendo que es el índice correspondiente en tus tabs)
    with tabs[len(grupos_unicos) + 1]:
        st.subheader("Modelación Cinética y Parámetros de Transferencia")
        sub_vista = st.selectbox(
            "Selecciona el apartado a visualizar:",
            [
                "Tabla Resumen de Kapp, t50 y t80",
                "Gráfica Cinética con t50 y t80",
                "Mapa de Calor (Temperatura vs Agitación)"
            ]
        )
        
        if sub_vista == "Tabla Resumen de Kapp, t50 y t80":
            with st.expander("Ver Tabla Resumen de $k_{app}$ y $R^2$", expanded=True):
                        tabla_kapp_datos = []
                        for g_nombre in grupos_unicos:
                            d_g = datos_agrupados[g_nombre]
                            tabla_kapp_datos.append({
                                "Grupo / Condición": g_nombre,
                                "k_app (1/min)": f"{d_g['Kapp']:.4f}",
                                "R2 del ajuste cinético": f"{d_g['RK']:.4f}",
                                "t50 (min)": f"{d_g['t50']:.2f}",
                                "t80 (min)": f"{d_g['t80']:.2f}"
                            })
                        st.dataframe(pd.DataFrame(tabla_kapp_datos), use_container_width=True)
                        
            pass
        elif sub_vista == "Gráfica Cinética con t50 y t80":
            st.write("#### Perfil Cinético y Tiempos Característicos ($t_{50}$ y $t_{80}$)")
            
            fig_kin, ax_kin = plt.subplots(figsize=(9, 5))
            C_ref = 5.20  # Tu concentración de referencia o equilibrio (C_infinito)
            t_teorico = np.linspace(0, max(tiempos_muestreo), 100)
            
            # Graficamos las líneas horizontales de referencia para el 50% y 80% como en la diapo 18
            ax_kin.axhline(y=0.5 * C_ref, color='orange', linestyle=':', alpha=0.7, label=f"50% C_ref ({0.5 * C_ref} mg/mL)")
            ax_kin.axhline(y=0.8 * C_ref, color='blue', linestyle=':', alpha=0.7, label=f"80% C_ref ({0.8 * C_ref} mg/mL)")
            ax_kin.axhline(y=C_ref, color='red', linestyle='--', alpha=0.6, label=f"C_ref (Equilibrio) = {C_ref} mg/mL")
            
            for grupo in grupos_unicos:
                d_g = datos_agrupados[grupo]
                k_val = d_g["Kapp"]
                
                # 1. Puntos experimentales (Promedio de las réplicas)
                ax_kin.plot(
                    d_g["Tiempos"], d_g["ConcProm"], label=f"{grupo} (Experimental)"
                )        
                    # Opcional: Calcular y marcar los puntos exactos de t50 y t80 para este grupo
            t_50 = np.log(2) / kapp
            t_80 = np.log(5) / kapp
                    # Puedes imprimir o mostrar estos valores en tu reporte
                    
            ax_kin.set_xlabel("Tiempo (min)")
            ax_kin.set_ylabel("Concentración (mg/mL)")
            ax_kin.set_title("Cinética de Diálisis: Ajuste al Modelo y Tiempos Característicos")
            ax_kin.grid(True)
            ax_kin.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
            plt.tight_layout()
            st.pyplot(fig_kin)
            pass
            
        elif sub_vista == "Mapa de Calor (Temperatura vs Agitación)":
                st.write("#### Mapa de Calor: Interacción de Temperatura y Agitación ($k_{app}$)")
                
                
                import re

                matriz_datos = []
                
                # Depuración: muestra las claves disponibles para verificar si están todas
                # st.write("Grupos encontrados en memoria:", list(datos_agrupados.keys()))
                
                for g_nombre, d_g in datos_agrupados.items():
                    k_val = d_g.get("Kapp", 0.0)
                    
                    temp = None
                    rpm = None
                    
                    # Intentamos extraer todos los números del nombre del grupo
                    nums = re.findall(r"[-+]?\d*\.\d+|\d+", str(g_nombre))
                    
                    if len(nums) >= 2:
                        # Asumimos que el primer número es la temperatura y el segundo es la RPM
                        temp = float(nums[0])
                        rpm = float(nums[1])
                    else:
                        # Si tus nombres no tienen los números, puedes buscarlos en el diccionario d_g
                        temp = d_g.get("temperatura", None)
                        rpm = d_g.get("rpm", None)
                        
                    if temp is not None and rpm is not None:
                        matriz_datos.append({"Temperatura": temp, "RPM": rpm, "Kapp": k_val})

                df_heatmap = pd.DataFrame(matriz_datos)
                
                if not df_heatmap.empty and len(df_heatmap) > 1:
                    # Creamos la tabla pivote con todas las temperaturas y RPM recopiladas
                    pivote = df_heatmap.pivot(index="RPM", columns="Temperatura", values="Kapp")
                    
                    fig_hm, ax_hm = plt.subplots(figsize=(8, 5))
                    cax = ax_hm.imshow(pivote.values, cmap="plasma", aspect="auto", origin="lower")
                    
                    ax_hm.set_xticks(np.arange(len(pivote.columns)))
                    ax_hm.set_yticks(np.arange(len(pivote.index)))
                    ax_hm.set_xticklabels([f"{t} °C" for t in pivote.columns])
                    ax_hm.set_yticklabels([f"{r} rpm" for r in pivote.index])
                    
                    ax_hm.set_xlabel("Temperatura (°C)")
                    ax_hm.set_ylabel("Agitación (RPM)")
                    ax_hm.set_title("Mapa de Calor: $k_{app}$ según Temperatura y Agitación")
                    
                    cbar = fig_hm.colorbar(cax)
                    cbar.set_label("$k_{app}$ (1/min)")
                    
                    # Anotar los valores numéricos en cada celda de la cuadrícula
                    for i in range(len(pivote.index)):
                        for j in range(len(pivote.columns)):
                            val = pivote.values[i, j]
                            if not np.isnan(val):
                                ax_hm.text(j, i, f"{val:.4f}", ha="center", va="center", color="black", fontweight="bold")
                                
                    plt.tight_layout()
                    st.pyplot(fig_hm)
                else:
                    st.warning(f"Se detectó solo {len(df_heatmap)} condición(es). El mapa de calor requiere múltiples condiciones (temperaturas y RPM) para generar la cuadrícula. Revisa cómo se están guardando los nombres en `datos_agrupados`.")
                     matriz_datos = []
                
                # Depuración: muestra las claves disponibles para verificar si están todas
                # st.write("Grupos encontrados en memoria:", list(datos_agrupados.keys()))
                
                for g_nombre, d_g in datos_agrupados.items():
                    t_80 = d_g.get("t80", 0.0)
                    
                    temp = None
                    rpm = None
                    
                    # Intentamos extraer todos los números del nombre del grupo
                    nums = re.findall(r"[-+]?\d*\.\d+|\d+", str(g_nombre))
                    
                    if len(nums) >= 2:
                        # Asumimos que el primer número es la temperatura y el segundo es la RPM
                        temp = float(nums[0])
                        rpm = float(nums[1])
                    else:
                        # Si tus nombres no tienen los números, puedes buscarlos en el diccionario d_g
                        temp = d_g.get("temperatura", None)
                        rpm = d_g.get("rpm", None)
                        
                    if temp is not None and rpm is not None:
                        matriz_datos.append({"Temperatura": temp, "RPM": rpm, "t80": t_80})

                df_heatmap = pd.DataFrame(matriz_datos)
                
                if not df_heatmap.empty and len(df_heatmap) > 1:
                    # Creamos la tabla pivote con todas las temperaturas y RPM recopiladas
                    pivote = df_heatmap.pivot(index="RPM", columns="Temperatura", values="t80")
                    
                    fig_hm, ax_hm = plt.subplots(figsize=(8, 5))
                    cax = ax_hm.imshow(pivote.values, cmap="plasma", aspect="auto", origin="lower")
                    
                    ax_hm.set_xticks(np.arange(len(pivote.columns)))
                    ax_hm.set_yticks(np.arange(len(pivote.index)))
                    ax_hm.set_xticklabels([f"{t} °C" for t in pivote.columns])
                    ax_hm.set_yticklabels([f"{r} rpm" for r in pivote.index])
                    
                    ax_hm.set_xlabel("Temperatura (°C)")
                    ax_hm.set_ylabel("Agitación (RPM)")
                    ax_hm.set_title("Mapa de Calor: $T_{80}$ según Temperatura y Agitación")
                    
                    cbar = fig_hm.colorbar(cax)
                    cbar.set_label("$T_{80}$")
                    
                    # Anotar los valores numéricos en cada celda de la cuadrícula
                    for i in range(len(pivote.index)):
                        for j in range(len(pivote.columns)):
                            val = pivote.values[i, j]
                            if not np.isnan(val):
                                ax_hm.text(j, i, f"{val:.4f}", ha="center", va="center", color="black", fontweight="bold")
                                
                    plt.tight_layout()
                    st.pyplot(fig_hm)
                else:
                    st.warning(f"Se detectó solo {len(df_heatmap)} condición(es). El mapa de calor requiere múltiples condiciones (temperaturas y RPM) para generar la cuadrícula. Revisa cómo se están guardando los nombres en `datos_agrupados`.")

