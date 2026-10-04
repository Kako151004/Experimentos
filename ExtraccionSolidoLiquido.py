import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Cinética de Extracción y Calibración", page_icon="🍇", layout="wide"
)

st.title("🍇 Cinética de Extracción Sólido-Líquido y Curva de Calibrado")
st.markdown(
    """
    Esta aplicación procesa los datos experimentales para el análisis cinético de procesos de extracción 
    sólido-líquido. Permite gestionar un **número dinámico de réplicas** por condición, construir la curva de calibrado, 
    calcular promedios, desviaciones estándar, coeficientes de variación, velocidades aparentes, 
    visualizar gráficos individuales con desviación y gráficos de barras comparativos.
    """
)

# Inicializar historial en la sesión para réplicas dinámicas
if "historial_condiciones" not in st.session_state:
    st.session_state.historial_condiciones = {}

# --- 1. SECCIÓN DE CURVA DE CALIBRADO ---
st.sidebar.header("📈 1. Curva de Calibrado")
st.sidebar.markdown("Ingrese los valores para calcular la recta de calibración ($A = m \cdot C + b$):")

input_conc_std = st.sidebar.text_area("Concentraciones estándar (ppm o mg/L)", "0.0 5.0 10.0 15.0 20.0")
input_abs_std = st.sidebar.text_area("Absorbancias de los estándares ($A_{600}$)", "0.00 0.15 0.31 0.46 0.60")

try:
    conc_std = np.array([float(x) for x in input_conc_std.split()])
    abs_std = np.array([float(x) for x in input_abs_std.split()])
    
    if len(conc_std) == len(abs_std) and len(conc_std) > 1:
        m, b = np.polyfit(conc_std, abs_std, 1)
        p = np.poly1d([m, b])
        y_fit = p(conc_std)
        ss_res = np.sum((abs_std - y_fit)**2)
        ss_tot = np.sum((abs_std - np.mean(abs_std))**2)
        r2 = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0.0
    else:
        m, b, r2 = 1.0, 0.0, 0.0
except:
    m, b, r2 = 1.0, 0.0, 0.0

st.sidebar.success(f"Ecuación: A = {m:.4f}C + {b:.4f} | R² = {r2:.4f}")

st.sidebar.markdown("---")
st.sidebar.header("⚙️ 2. Parámetros de Extracción")
input_tiempos = st.sidebar.text_area(
    "Tiempos de muestreo (min) (separados por espacio)", "0 5 10 15 30"
)

try:
    tiempos = np.array([float(x) for x in input_tiempos.split()])
except:
    tiempos = np.array([0.0, 5.0, 10.0, 15.0, 30.0])

st.sidebar.markdown("---")
st.sidebar.header("🧪 3. Registro Dinámico de Réplicas")

frutas_disponibles = ["Manzana", "Pera", "Durazno/Nectarina", "Kiwi", "Frutos Rojos", "Otra Fruta"]
fruta_sel = st.sidebar.selectbox("Seleccione la Fruta / Matriz", frutas_disponibles)
agitacion_sel = st.sidebar.selectbox("Condición de Agitación", ["Sin Agitación (0 rpm)", "Con Agitación (200 rpm)"])

condicion_nombre = f"{fruta_sel} - {agitacion_sel}"
st.sidebar.info(f"Condición seleccionada: **{condicion_nombre}**")

replicas_actuales = st.session_state.historial_condiciones.get(condicion_nombre, [])
st.sidebar.write(f"📝 Réplicas guardadas para esta condición: **{len(replicas_actuales)}**")

input_nueva_replica = st.sidebar.text_area("Absorbancias de la nueva réplica", "0.05 0.12 0.18 0.22 0.25")

col_b1, col_b2, col_b3 = st.sidebar.columns(3)
add_rep = col_b1.button("➕ Añadir Réplica")
reset_cond = col_b2.button("🔄 Borrar Condición")
limpiar_todo = col_b3.button("🗑️ Limpiar Todo")

if limpiar_todo:
    st.session_state.historial_condiciones = {}
    st.success("Se ha reiniciado todo el historial.")
    st.rerun()

if reset_cond:
    if condicion_nombre in st.session_state.historial_condiciones:
        del st.session_state.historial_condiciones[condicion_nombre]
        st.success(f"Se borraron las réplicas de **{condicion_nombre}**.")
        st.rerun()

if add_rep:
    try:
        arr_rep = np.array([float(x) for x in input_nueva_replica.split()])
        if len(arr_rep) != len(tiempos):
            st.sidebar.error("⚠️ La cantidad de valores de absorbancia debe coincidir exactamente con los tiempos.")
        else:
            if condicion_nombre not in st.session_state.historial_condiciones:
                st.session_state.historial_condiciones[condicion_nombre] = []
            st.session_state.historial_condiciones[condicion_nombre].append(arr_rep)
            st.sidebar.success(f"✅ Réplica #{len(st.session_state.historial_condiciones[condicion_nombre])} añadida con éxito a **{condicion_nombre}**.")
    except Exception as e:
        st.sidebar.error(f"Error al procesar la réplica: {e}")

# --- PANTALLA PRINCIPAL ---
st.markdown("---")
st.header("📊 Análisis de Resultados y Curva de Calibrado")

col_c1, col_c2 = st.columns([1, 1])
with col_c1:
    st.subheader("📈 Gráfica de la Curva de Calibrado")
    fig_cal, ax_cal = plt.subplots(figsize=(6, 4))
    ax_cal.scatter(conc_std, abs_std, color="purple", label="Estándares experimentales", zorder=5)
    
    x_line = np.linspace(min(conc_std), max(conc_std), 100)
    ax_cal.plot(x_line, m * x_line + b, color="orange", linestyle="--", label=f"A = {m:.4f}C + {b:.4f}\nR² = {r2:.4f}")
    
    ax_cal.set_xlabel("Concentración")
    ax_cal.set_ylabel("Absorbancia ($A_{600}$)")
    ax_cal.set_title("Curva de Calibración")
    ax_cal.grid(True, linestyle="--", alpha=0.6)
    ax_cal.legend()
    st.pyplot(fig_cal)

with col_c2:
    st.subheader("📝 Parámetros de la Recta")
    st.markdown("La regresión lineal obtenida permite transformar la absorbancia en **concentraciones**:")
    st.latex(r"C = \frac{A - b}{m}")
    
    st.markdown(
        f"""
        * **Pendiente ($m$):** `{m:.5f}`
        * **Intercepción ($b$):** `{b:.5f}`
        * **Coeficiente de Correlación ($R^2$):** `{r2:.4f}`
        """
    )
    df_cal_tabla = pd.DataFrame({
        "Concentración Estándar": conc_std,
        "Absorbancia Medida": abs_std
    })
    st.dataframe(df_cal_tabla, use_container_width=True)

# --- PROCESAMIENTO CINÉTICO ---
historial = st.session_state.historial_condiciones

if len(historial) > 0:
    st.markdown("---")
    st.header("📋 Cinética de Extracción por Muestra")
    st.markdown(
        """
        Se procesan todas las condiciones que tengan réplicas registradas, calculando automáticamente 
        los promedios, la desviación estándar muestral ($s$), el coeficiente de variación ($CV\%$), 
        la concentración y el gráfico específico con barras de error para cada sección.
        """
    )

    datos_procesados = {}
    for cond, lista_reps in historial.items():
        if len(lista_reps) == 0:
            continue
        
        matriz_reps = np.array(lista_reps)
        a_prom = np.mean(matriz_reps, axis=0)
        
        if len(lista_reps) > 1:
            s_val = np.std(matriz_reps, axis=0, ddof=1)
        else:
            s_val = np.zeros_like(a_prom)

        cv_val = np.divide(s_val, a_prom, out=np.zeros_like(s_val), where=a_prom!=0) * 100

        if m != 0:
            c_prom = (a_prom - b) / m
        else:
            c_prom = np.zeros_like(a_prom)

        a_inicial = a_prom[0]
        a_final = a_prom[-1]
        denominador_erel = a_final - a_inicial
        if denominador_erel != 0:
            erel_val = ((a_prom - a_inicial) / denominador_erel) * 100
        else:
            erel_val = np.zeros_like(a_prom)

        dt = np.diff(tiempos)
        da = np.diff(a_prom)
        r_a = np.divide(da, dt, out=np.zeros_like(da), where=dt!=0)

        partes = cond.split(" - ")
        fruta = partes[0]
        agitacion = " - ".join(partes[1:])

        datos_procesados[cond] = {
            "Fruta": fruta,
            "Agitacion": agitacion,
            "Tiempos": tiempos,
            "MatrizReps": matriz_reps,
            "AProm": a_prom,
            "CProm": c_prom,
            "S": s_val,
            "CV": cv_val,
            "ERel": erel_val,
            "Velocidades": r_a,
            "IntervalosVel": [f"{int(ti)} a {int(tf)} min" for ti, tf in zip(tiempos[:-1], tiempos[1:])]
        }

    nombres_conds = list(datos_procesados.keys())
    tabs = st.tabs([f"🍇 {c}" for c in nombres_conds] + ["⚡ Análisis de Agitación", "📈 Gráfica Global & Barras"])

    # Pestañas individuales por condición con su gráfica de desviación y controles
    for idx, cond in enumerate(nombres_conds):
        d = datos_procesados[cond]
        with tabs[idx]:
            st.markdown(f"### Condición evaluada: **{cond}**")
            st.markdown(f"Total de réplicas analizadas: **{len(d['MatrizReps'])}**")
            
            dict_tabla = {"Tiempo (min)": d["Tiempos"]}
            for i, rep_vals in enumerate(d["MatrizReps"]):
                dict_tabla[f"Réplica {i+1} ($A$)"] = rep_vals
            
            dict_tabla["Promedio ($\overline{A}$)"] = [f"{v:.4f}" for v in d["AProm"]]
            dict_tabla["Desv. Estándar ($s$)"] = [f"{v:.4f}" for v in d["S"]]
            dict_tabla["CV (%)"] = [f"{v:.2f}%" for v in d["CV"]]
            dict_tabla["Concentración ($\overline{C}$)"] = [f"{v:.4f}" for v in d["CProm"]]
            dict_tabla["Extracción Relativa ($E_{rel}\%$)"] = [f"{v:.2f}%" for v in d["ERel"]]

            st.markdown("#### 📊 Tabla Principal: Réplicas, Promedios y Concentración")
            df_principal = pd.DataFrame(dict_tabla)
            st.dataframe(df_principal, use_container_width=True)

            st.markdown("#### ⚡ Tabla Secundaria: Velocidad Aparente de Extracción ($r_A = \Delta A / \Delta t$)")
            if len(d["Tiempos"]) > 1:
                df_vel = pd.DataFrame({
                    "Intervalo de tiempo (min)": d["IntervalosVel"],
                    "Velocidad Aparente $r_A$ (Abs/min)": [f"{v:.6f}" for v in d["Velocidades"]]
                })
                st.dataframe(df_vel, use_container_width=True)
            else:
                st.info("Se requieren al menos 2 tiempos de muestreo para calcular las velocidades.")

            st.markdown("#### 📉 Gráfica Individual de la Condición (con Desviación Estándar)")
            
            # Checkbox para personalizar la visualización de la sección
            mostrar_barras_error = st.checkbox(f"Mostrar barras de desviación estándar ({cond})", value=True, key=f"chk_{cond}")
            
            fig_ind, ax_ind = plt.subplots(figsize=(8, 4))
            if mostrar_barras_error:
                ax_ind.errorbar(d["Tiempos"], d["AProm"], yerr=d["S"], fmt="-o", capsize=4, color="purple", label="Promedio $\pm$ s")
            else:
                ax_ind.plot(d["Tiempos"], d["AProm"], "-o", color="purple", label="Promedio")
                
            ax_ind.set_xlabel("Tiempo (min)")
            ax_ind.set_ylabel("Absorbancia Promedio ($A_{600}$)")
            ax_ind.set_title(f"Cinética de Extracción: {cond}")
            ax_ind.grid(True, linestyle="--", alpha=0.6)
            ax_ind.legend()
            st.pyplot(fig_ind)

    # Pestaña de Análisis Comparativo de Agitación
    with tabs[len(nombres_conds)]:
        st.markdown("### ⚡ Efecto de la Agitación (Sin Agitación vs Con Agitación)")
        st.markdown("Evaluación del impacto hidrodinámico comparando los promedios por tipo de muestra vegetal.")

        frutas_registradas = list(set([d["Fruta"] for d in datos_procesados.values()]))
        comparaciones_encontradas = False

        for fruta in frutas_registradas:
            cond_estatica = f"{fruta} - Sin Agitación (0 rpm)"
            cond_agitada = f"{fruta} - Con Agitación (200 rpm)"

            if cond_estatica in datos_procesados and cond_agitada in datos_procesados:
                comparaciones_encontradas = True
                st.markdown(f"#### 🍇 Fruta analizada: **{fruta}**")

                a_0 = datos_procesados[cond_estatica]["AProm"]
                a_200 = datos_procesados[cond_agitada]["AProm"]
                t_arr = datos_procesados[cond_estatica]["Tiempos"]

                delta_a = a_200 - a_0
                e_agit = np.divide(delta_a, a_0, out=np.zeros_like(a_0), where=a_0!=0) * 100

                df_agit = pd.DataFrame({
                    "Tiempo (min)": t_arr,
                    "Promedio Sin Agitación ($\overline{A}_0$)": [f"{v:.4f}" for v in a_0],
                    "Promedio Con Agitación ($\overline{A}_{200}$)": [f"{v:.4f}" for v in a_200],
                    "Diferencia Absoluta ($\Delta A_{agit}$)": [f"{v:.4f}" for v in delta_a],
                    "Efecto Porcentual ($E_{agit}\%$)": [f"{v:.2f}%" for v in e_agit]
                })
                st.dataframe(df_agit, use_container_width=True)
                st.markdown("---")

        if not comparaciones_encontradas:
            st.warning("⚠️ Para visualizar esta sección, registra al menos una fruta evaluando ambas condiciones (Sin Agitación y Con Agitación).")

    # Pestaña de Gráfica Global y Gráfico de Barras
    with tabs[len(nombres_conds) + 1]:
        st.markdown("### 📈 Gráfica Global de Cinética de Extracción")
        st.markdown("Evolución temporal de la concentración promedio obtenida a través de la curva de calibrado para todas las condiciones.")
        
        fig, ax = plt.subplots(figsize=(10, 5))
        for cond, d in datos_procesados.items():
            ax.plot(
                d["Tiempos"],
                d["CProm"],
                marker="o",
                linewidth=2,
                label=cond
            )

        ax.set_xlabel("Tiempo (min)", fontsize=12)
        ax.set_ylabel("Concentración Promedio", fontsize=12)
        ax.set_title("Cinética Global de Extracción (Concentración vs Tiempo)", fontsize=14)
        ax.grid(True, linestyle="--", alpha=0.7)
        ax.legend(bbox_to_anchor=(1.05, 1), loc="upper left")
        plt.tight_layout()
        st.pyplot(fig)

        st.markdown("---")
        st.markdown("### 📊 Gráfico de Barras Comparativo (Concentración Final)")
        st.markdown("Comparación directa de la concentración alcanzada en el último tiempo de muestreo para cada condición registrada.")
        
        condiciones_nombres = list(datos_procesados.keys())
        concentraciones_finales = [datos_procesados[c]["CProm"][-1] for c in condiciones_nombres]
        
        fig_bar, ax_bar = plt.subplots(figsize=(10, 4))
        barras = ax_bar.bar(condiciones_nombres, concentraciones_finales, color=["purple", "orange", "teal", "crimson", "royalBlue"][:len(condiciones_nombres)])
        ax_bar.set_ylabel("Concentración Final")
        ax_bar.set_title("Comparativa de Concentración Final por Condición")
        ax_bar.grid(axis="y", linestyle="--", alpha=0.6)
        plt.xticks(rotation=20, ha="right")
        
        # Añadir etiquetas de valor encima de las barras
        for barra in barras:
            yval = barra.get_height()
            ax_bar.text(barra.get_x() + barra.get_width()/2.0, yval + 0.01, f"{yval:.2f}", ha='center', va='bottom')
            
        plt.tight_layout()
        st.pyplot(fig_bar)

else:
    st.info("👈 Ingresa los datos de tu curva de calibrado y añade al menos una réplica en la barra lateral para iniciar el análisis.")
