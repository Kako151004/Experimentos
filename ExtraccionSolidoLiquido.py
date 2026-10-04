import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Cinética de Extracción Sólido-Líquido", page_icon="🍇", layout="wide"
)

st.title("🍇 Cinética de Extracción Sólido-Líquido")
st.markdown(
    """
    Esta aplicación procesa datos experimentales de absorbancia para el análisis cinético de procesos 
    de extracción sólido-líquido. Permite gestionar réplicas experimentales, calcular promedios, 
    desviaciones estándar, coeficientes de variación, velocidades aparentes de extracción, efectos de agitación 
    y la extracción relativa normalizada.
    """
)

# Inicializar historial en la sesión
if "historial" not in st.session_state:
    st.session_state.historial = []

# Configuración en la barra lateral
st.sidebar.header("⚙️ Parámetros Generales")
input_tiempos = st.sidebar.text_area(
    "Tiempos de muestreo (min) (separados por espacio)", "0 5 10 15 30"
)

try:
    tiempos = np.array([float(x) for x in input_tiempos.split()])
except:
    tiempos = np.array([0.0, 5.0, 10.0, 15.0, 30.0])

st.sidebar.markdown("---")
st.sidebar.header("🧪 Registro de Réplicas por Condición")

matrices_disponibles = ["Muestra 1", "Muestra 2", "Muestra 3", "Muestra 4", "Otra Muestra"]
matriz_sel = st.sidebar.selectbox("Seleccione la Matriz / Muestra", matrices_disponibles)
agitacion_sel = st.sidebar.selectbox("Condición de Agitación", ["Sin Agitación (0 rpm)", "Con Agitación"])

condicion_nombre = f"{matriz_sel} - {agitacion_sel}"
st.sidebar.info(f"Registrando triplicado para: **{condicion_nombre}**")

st.sidebar.markdown("Ingrese los valores experimentales de absorbancia o respuesta para las tres réplicas en los tiempos definidos:")
abs_r1_input = st.sidebar.text_area("Réplica 1 ($R_1$)", "0.05 0.12 0.18 0.22 0.25")
abs_r2_input = st.sidebar.text_area("Réplica 2 ($R_2$)", "0.06 0.13 0.17 0.23 0.26")
abs_r3_input = st.sidebar.text_area("Réplica 3 ($R_3$)", "0.05 0.11 0.19 0.21 0.24")

col_b1, col_b2 = st.sidebar.columns(2)
guardar = col_b1.button("💾 Guardar Condición")
limpiar = col_b2.button("🗑️️ Limpiar Todo")

if limpiar:
    st.session_state.historial = []
    st.success("Historial reiniciado correctamente.")

if guardar:
    try:
        arr_r1 = np.array([float(x) for x in abs_r1_input.split()])
        arr_r2 = np.array([float(x) for x in abs_r2_input.split()])
        arr_r3 = np.array([float(x) for x in abs_r3_input.split()])

        if len(arr_r1) != len(tiempos) or len(arr_r2) != len(tiempos) or len(arr_r3) != len(tiempos):
            st.sidebar.error("⚠️ La cantidad de valores debe coincidir exactamente con la cantidad de tiempos.")
        else:
            # Reemplazar si ya existe la condición o agregarla
            st.session_state.historial = [h for h in st.session_state.historial if h["Condicion"] != condicion_nombre]
            
            st.session_state.historial.append({
                "Condicion": condicion_nombre,
                "Matriz": matriz_sel,
                "Agitacion": agitacion_sel,
                "R1": arr_r1,
                "R2": arr_r2,
                "R3": arr_r3
            })
            st.sidebar.success(f"✅ Condición **{condicion_nombre}** guardada con éxito.")
    except Exception as e:
        st.sidebar.error(f"Error al procesar los datos: {e}")

# --- PROCESAMIENTO Y VISUALIZACIÓN DE DATOS ---
historial = st.session_state.historial

if len(historial) > 0:
    st.markdown("---")
    st.header("📋 Resultados y Análisis Estadístico")
    st.markdown(
        """
        A continuación se presentan las tablas detalladas con los cálculos correspondientes al promedio, 
        la desviación estándar muestral ($s$), el coeficiente de variación ($CV\%$), la velocidad aparente 
        de extracción ($r_A$) y la extracción relativa normalizada ($E_{rel}\%[cite: 2, 3]$).
        """
    )

    datos_procesados = {}
    for item in historial:
        cond = item["Condicion"]
        r1_arr = item["R1"]
        r2_arr = item["R2"]
        r3_arr = item["R3"]

        # 1. Promedio: Prom = (R1 + R2 + R3) / 3[cite: 1, 2]
        val_prom = (r1_arr + r2_arr + r3_arr) / 3.0

        # 2. Desviación estándar muestral: s = sqrt(sum((Ri - Prom)^2) / (n - 1)) con n=3[cite: 1, 2]
        suma_cuad = (r1_arr - val_prom)**2 + (r2_arr - val_prom)**2 + (r3_arr - val_prom)**2
        s_val = np.sqrt(suma_cuad / 2.0)

        # 3. Coeficiente de variación: CV(%) = (s / Prom) * 100[cite: 1, 2]
        cv_val = np.divide(s_val, val_prom, out=np.zeros_like(s_val), where=val_prom!=0) * 100

        # 4. Extracción relativa corregida: Erel(%) = [(Val_t - Val_inicial) / (Val_final - Val_inicial)] * 100[cite: 2, 3]
        val_inicial = val_prom[0]
        val_final = val_prom[-1]
        denominador_erel = val_final - val_inicial
        if denominador_erel != 0:
            erel_val = ((val_prom - val_inicial) / denominador_erel) * 100
        else:
            erel_val = np.zeros_like(val_prom)

        # 5. Velocidad aparente de extracción: r = delta Val / delta t[cite: 2, 3]
        dt = np.diff(tiempos)
        dval = np.diff(val_prom)
        r_val = np.divide(dval, dt, out=np.zeros_like(dval), where=dt!=0)

        datos_procesados[cond] = {
            "Matriz": item["Matriz"],
            "Agitacion": item["Agitacion"],
            "Tiempos": tiempos,
            "R1": r1_arr,
            "R2": r2_arr,
            "R3": r3_arr,
            "ValProm": val_prom,
            "S": s_val,
            "CV": cv_val,
            "ERel": erel_val,
            "Velocidades": r_val,
            "IntervalosVel": [f"{int(ti)} a {int(tf)}" for ti, tf in zip(tiempos[:-1], tiempos[1:])]
        }

    nombres_conds = list(datos_procesados.keys())
    tabs = st.tabs([f"🍇 {c}" for c in nombres_conds] + ["⚡ Análisis de Agitación", "📈 Gráfica Global"])

    # Pestañas individuales por condición
    for idx, cond in enumerate(nombres_conds):
        d = datos_procesados[cond]
        with tabs[idx]:
            st.markdown(f"### Condición evaluada: **{cond}**")
            st.markdown("Esta sección detalla los valores experimentales de las tres réplicas y sus parámetros estadísticos asociados.")
            
            st.markdown("#### 📊 Tabla Principal: Promedios, Desviación Estándar y Extracción Relativa")
            df_principal = pd.DataFrame({
                "Tiempo (min)": d["Tiempos"],
                "Réplica 1 ($R_1$)": d["R1"],
                "Réplica 2 ($R_2$)": d["R2"],
                "Réplica 3 ($R_3$)": d["R3"],
                "Promedio ($\overline{X}$)": [f"{v:.4f}" for v in d["ValProm"]],
                "Desv. Estándar ($s$)": [f"{v:.4f}" for v in d["S"]],
                "CV (%)": [f"{v:.2f}%" for v in d["CV"]],
                "Extracción Relativa ($E_{rel}\%$)": [f"{v:.2f}%" for v in d["ERel"]]
            })
            st.dataframe(df_principal, use_container_width=True)

            st.markdown("#### ⚡ Tabla Secundaria: Velocidad Aparente de Extracción ($r = \Delta X / \Delta t$)")
            st.markdown("Mide la rapidez de cambio de la variable promedio entre intervalos de tiempo consecutivos[cite: 2, 3].")
            if len(d["Tiempos"]) > 1:
                df_vel = pd.DataFrame({
                    "Intervalo de tiempo (min)": d["IntervalosVel"],
                    "Velocidad Aparente $r$ (Unidades/min)": [f"{v:.6f}" for v in d["Velocidades"]]
                })
                st.dataframe(df_vel, use_container_width=True)
            else:
                st.info("Se requieren al menos 2 tiempos de muestreo para calcular las velocidades.")

    # Pestaña de Análisis Comparativo de Agitación
    with tabs[len(nombres_conds)]:
        st.markdown("### ⚡ Efecto de la Agitación (Sin Agitación vs Con Agitación)")
        st.markdown(
            """
            Evaluación del impacto hidrodinámico mediante la diferencia absoluta ($\Delta X_{agit} = \overline{X}_{agitada} - \overline{X}_{estatica}$) 
            y el efecto porcentual de la agitación ($E_{agit}\%[cite: 2, 3]$).
            """
        )

        matrices_registradas = list(set([d["Matriz"] for d in datos_procesados.values()]))
        comparaciones_encontradas = False

        for matriz in matrices_registradas:
            cond_estatica = f"{matriz} - Sin Agitación (0 rpm)"
            cond_agitada = f"{matriz} - Con Agitación"

            if cond_estatica in datos_procesados and cond_agitada in datos_procesados:
                comparaciones_encontradas = True
                st.markdown(f"#### 🍇 Muestra analizada: **{matriz}**")

                val_0 = datos_procesados[cond_estatica]["ValProm"]
                val_agit = datos_procesados[cond_agitada]["ValProm"]
                t_arr = datos_procesados[cond_estatica]["Tiempos"]

                delta_val = val_agit - val_0
                e_agit = np.divide(delta_val, val_0, out=np.zeros_like(val_0), where=val_0!=0) * 100

                df_agit = pd.DataFrame({
                    "Tiempo (min)": t_arr,
                    "Promedio Estático ($\overline{X}_0$)": [f"{v:.4f}" for v in val_0],
                    "Promedio Agitado ($\overline{X}_{agit}$)": [f"{v:.4f}" for v in val_agit],
                    "Diferencia Absoluta ($\Delta X_{agit}$)": [f"{v:.4f}" for v in delta_val],
                    "Efecto Porcentual ($E_{agit}\%$)": [f"{v:.2f}%" for v in e_agit]
                })
                st.dataframe(df_agit, use_container_width=True)
                st.markdown("---")

        if not comparaciones_encontradas:
            st.warning("⚠️ Para visualizar esta sección, registre al menos una muestra evaluando ambas condiciones de agitación.")

    # Pestaña de Gráfica Global
    with tabs[len(nombres_conds) + 1]:
        st.markdown("### 📈 Gráfica Global de Cinética de Extracción")
        st.markdown("Representación temporal de los valores promedio incorporando las barras de error correspondientes a la desviación estándar ($s$[cite: 1, 2]).")
        
        fig, ax = plt.subplots(figsize=(10, 6))
        for cond, d in datos_procesados.items():
            ax.errorbar(
                d["Tiempos"],
                d["ValProm"],
                yerr=d["S"],
                fmt="-o",
                capsize=4,
                linewidth=2,
                label=cond
            )

        ax.set_xlabel("Tiempo (min)", fontsize=12)
        ax.set_ylabel("Valor Promedio (adimensional / unidades)", fontsize=12)
        ax.set_title("Cinética de Extracción Sólido-Líquido (Promedio ± Desviación Estándar)", fontsize=14)
        ax.grid(True, linestyle="--", alpha=0.7)
        ax.legend(bbox_to_anchor=(1.05, 1), loc="upper left")
        plt.tight_layout()
        st.pyplot(fig)

else:
    st.info("👈 Por favor, ingresa y guarda al menos una condición en la barra lateral para iniciar el análisis cinético.")
