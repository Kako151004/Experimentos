import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Reporte Lab 2: Extracción Sólido-Líquido", page_icon="📊", layout="wide"
)

st.title("📊 Laboratorio de Operaciones Unitarias en Biotecnología - UTEM")
st.subheader("Cinética de Extracción Sólido-Líquido (Análisis basado en Absorbancia $A_{600}$)")

st.markdown(
    """
    Esta aplicación procesa los datos experimentales de absorbancia a 600 nm según las ecuaciones 
    oficiales del **Reporte de Laboratorio N°2** (Prof. Belén Ponce Martínez). Gestiona réplicas, 
    calcula promedios, desviaciones estándar, velocidades aparentes, efectos de agitación y extracción relativa.
    """
)

# Inicializar estado en la sesión
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

frutas_disponibles = ["Manzana", "Pera", "Durazno/Nectarina", "Kiwi", "Otra Fruta"]
fruta_sel = st.sidebar.selectbox("Seleccione la Fruta / Matriz", frutas_disponibles)
agitacion_sel = st.sidebar.selectbox("Condición de Agitación", ["Sin Agitación (0 rpm)", "Con Agitación (200 rpm)"])

condicion_nombre = f"{fruta_sel} - {agitacion_sel}"
st.sidebar.info(f"Registrando triplicado para: **{condicion_nombre}**")

st.sidebar.markdown("Ingrese los valores de absorbancia ($A_{600}$) separados por espacio para cada réplica en los tiempos definidos:")
abs_r1_input = st.sidebar.text_area("Absorbancias Réplica 1 ($A_1$)", "0.05 0.12 0.18 0.22 0.25")
abs_r2_input = st.sidebar.text_area("Absorbancias Réplica 2 ($A_2$)", "0.06 0.13 0.17 0.23 0.26")
abs_r3_input = st.sidebar.text_area("Absorbancias Réplica 3 ($A_3$)", "0.05 0.11 0.19 0.21 0.24")

col_b1, col_b2 = st.sidebar.columns(2)
guardar = col_b1.button("💾 Guardar Condición")
limpiar = col_b2.button("🗑️ Limpiar Todo")

if limpiar:
    st.session_state.historial = []
    st.success("Historial reiniciado correctamente.")

if guardar:
    try:
        arr_r1 = np.array([float(x) for x in abs_r1_input.split()])
        arr_r2 = np.array([float(x) for x in abs_r2_input.split()])
        arr_r3 = np.array([float(x) for x in abs_r3_input.split()])

        if len(arr_r1) != len(tiempos) or len(arr_r2) != len(tiempos) or len(arr_r3) != len(tiempos):
            st.sidebar.error("⚠️ La cantidad de valores de absorbancia debe coincidir exactamente con la cantidad de tiempos.")
        else:
            # Reemplazar si ya existe la condición o agregarla
            st.session_state.historial = [h for h in st.session_state.historial if h["Condicion"] != condicion_nombre]
            
            st.session_state.historial.append({
                "Condicion": condicion_nombre,
                "Fruta": fruta_sel,
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
    st.header("📋 Resultados y Tablas de Análisis (Guía UTEM)")

    datos_procesados = {}
    for item in historial:
        cond = item["Condicion"]
        r1_arr = item["R1"]
        r2_arr = item["R2"]
        r3_arr = item["R3"]

        # 1. Promedio de absorbancia: A_bar = (A1 + A2 + A3) / 3[cite: 1, 2]
        a_prom = (r1_arr + r2_arr + r3_arr) / 3.0

        # 2. Desviación estándar muestral: s = sqrt(sum((Ai - A_bar)^2) / (n - 1)) con n=3[cite: 1, 2]
        suma_cuad = (r1_arr - a_prom)**2 + (r2_arr - a_prom)**2 + (r3_arr - a_prom)**2
        s_val = np.sqrt(suma_cuad / 2.0)

        # 3. Coeficiente de variación: CV(%) = (s / A_bar) * 100[cite: 1, 2]
        cv_val = np.divide(s_val, a_prom, out=np.zeros_like(s_val), where=a_prom!=0) * 100

        # 4. Extracción relativa corregida: Erel(%) = [(At - A_inicial) / (A_30 - A_inicial)] * 100[cite: 2, 3]
        a_inicial = a_prom[0]
        a_final = a_prom[-1]
        denominador_erel = a_final - a_inicial
        if denominador_erel != 0:
            erel_val = ((a_prom - a_inicial) / denominador_erel) * 100
        else:
            erel_val = np.zeros_like(a_prom)

        # 5. Velocidad aparente de extracción: rA = delta A / delta t[cite: 2, 3]
        dt = np.diff(tiempos)
        da = np.diff(a_prom)
        r_a = np.divide(da, dt, out=np.zeros_like(da), where=dt!=0)

        datos_procesados[cond] = {
            "Fruta": item["Fruta"],
            "Agitacion": item["Agitacion"],
            "Tiempos": tiempos,
            "R1": r1_arr,
            "R2": r2_arr,
            "R3": r3_arr,
            "AProm": a_prom,
            "S": s_val,
            "CV": cv_val,
            "ERel": erel_val,
            "Velocidades": r_a,
            "IntervalosVel": [f"{int(ti)} - {int(tf)} min" for ti, tf in zip(tiempos[:-1], tiempos[1:])]
        }

    nombres_conds = list(datos_procesados.keys())
    tabs = st.tabs([f"🧪 {c}" for c in nombres_conds] + ["📊 Análisis de Agitación", "📈 Gráfica Global"])

    # Pestañas individuales por condición
    for idx, cond in enumerate(nombres_conds):
        d = datos_procesados[cond]
        with tabs[idx]:
            st.markdown(f"### Condición: **{cond}**")
            
            st.markdown("#### 1. Datos Experimentales y Estadísticos Básicos")
            df_principal = pd.DataFrame({
                "Tiempo (min)": d["Tiempos"],
                "Réplica 1": d["R1"],
                "Réplica 2": d["R2"],
                "Réplica 3": d["R3"],
                "Promedio (A)": [f"{v:.4f}" for v in d["AProm"]],
                "Desv. Estándar (s)": [f"{v:.4f}" for v in d["S"]],
                "CV (%)": [f"{v:.2f}%" for v in d["CV"]],
                "Extracción Relativa Erel (%)": [f"{v:.2f}%" for v in d["ERel"]]
            })
            st.dataframe(df_principal, use_container_width=True)

            st.markdown("#### 2. Velocidad Aparente de Extracción ($r_A = \Delta A / \Delta t$)")[cite: 2, 3]
            if len(d["Tiempos"]) > 1:
                df_vel = pd.DataFrame({
                    "Intervalo (min)": d["IntervalosVel"],
                    "Velocidad Aparente rA (Abs/min)": [f"{v:.6f}" for v in d["Velocidades"]]
                })
                st.dataframe(df_vel, use_container_width=True)
            else:
                st.info("Se requieren al menos 2 tiempos de muestreo para calcular velocidades.")

    # Pestaña de Análisis Comparativo de Agitación
    with tabs[len(nombres_conds)]:
        st.markdown("### ⚡ Efecto de la Agitación (0 rpm vs 200 rpm)")
        st.markdown("Cálculo de la diferencia absoluta ($\Delta A_{agit}$) y el efecto porcentual ($E_{agit}\%$)[cite: 2, 3].")

        frutas_registradas = list(set([d["Fruta"] for d in datos_procesados.values()]))
        comparaciones_encontradas = False

        for fruta in frutas_registradas:
            cond_0 = f"{fruta} - Sin Agitación (0 rpm)"
            cond_200 = f"{fruta} - Con Agitación (200 rpm)"

            if cond_0 in datos_procesados and cond_200 in datos_procesados:
                comparaciones_encontradas = True
                st.markdown(f"#### 🍎 Fruta: **{fruta}**")

                a_0 = datos_procesados[cond_0]["AProm"]
                a_200 = datos_procesados[cond_200]["AProm"]
                t_arr = datos_procesados[cond_0]["Tiempos"]

                delta_a = a_200 - a_0
                e_agit = np.divide(delta_a, a_0, out=np.zeros_like(a_0), where=a_0!=0) * 100

                df_agit = pd.DataFrame({
                    "Tiempo (min)": t_arr,
                    "Promedio 0 rpm": [f"{v:.4f}" for v in a_0],
                    "Promedio 200 rpm": [f"{v:.4f}" for v in a_200],
                    "Diferencia Absoluta ($\Delta A_{agit}$)": [f"{v:.4f}" for v in delta_a],
                    "Efecto Agitación ($E_{agit}\%$)": [f"{v:.2f}%" for v in e_agit]
                })
                st.dataframe(df_agit, use_container_width=True)
                st.markdown("---")

        if not comparaciones_encontradas:
            st.warning("⚠️ Registre al menos una fruta con ambas condiciones (**Sin Agitación** y **Con Agitación**) para visualizar esta tabla.")

    # Pestaña de Gráfica Global
    with tabs[len(nombres_conds) + 1]:
        st.markdown("### 📈 Gráfica Global de Cinética ($A_{600}$ vs Tiempo)")
        
        fig, ax = plt.subplots(figsize=(10, 6))
        for cond, d in datos_procesados.items():
            ax.errorbar(
                d["Tiempos"],
                d["AProm"],
                yerr=d["S"],
                fmt="-o",
                capsize=4,
                linewidth=2,
                label=cond
            )

        ax.set_xlabel("Tiempo (min)", fontsize=12)
        ax.set_ylabel("Absorbancia Promedio $A_{600}$ (adimensional)", fontsize=12)
        ax.set_title("Cinética de Extracción Sólido-Líquido (Promedio ± Desviación Estándar)", fontsize=14)
        ax.grid(True, linestyle="--", alpha=0.7)
        ax.legend(bbox_to_anchor=(1.05, 1), loc="upper left")
        plt.tight_layout()
        st.pyplot(fig)

else:
    st.info("👈 Por favor, ingrese y guarde al menos una condición en la barra lateral para comenzar el análisis.")
