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
    sólido-líquido. Incluye la construcción de la **curva de calibrado** mediante regresión lineal, 
    la gestión de réplicas por matriz vegetal, el cálculo de promedios, desviaciones estándar, 
    coeficientes de variación, velocidades aparentes de extracción y el efecto de la agitación.
    """
)

# Inicializar historial en la sesión
if "historial" not in st.session_state:
    st.session_state.historial = []

# --- 1. SECCIÓN DE CURVA DE CALIBRADO ---
st.sidebar.header("📈 1. Curva de Calibrado")
st.sidebar.markdown("Ingrese los valores para calcular la recta de calibración ($A = m \cdot C + b$):")

input_conc_std = st.sidebar.text_area("Concentraciones estándar (ppm o mg/L)", "0.0 5.0 10.0 15.0 20.0")
input_abs_std = st.sidebar.text_area("Absorbancias de los estándares ($A_{600}$)", "0.00 0.15 0.31 0.46 0.60")

try:
    conc_std = np.array([float(x) for x in input_conc_std.split()])
    abs_std = np.array([float(x) for x in input_abs_std.split()])
    
    if len(conc_std) == len(abs_std) and len(conc_std) > 1:
        # Regresión lineal (grado 1)
        m, b = np.polyfit(conc_std, abs_std, 1)
        # Coeficiente de determinación R^2
        p = np.poly1d([m, b])
        y_fit = p(conc_std)
        ss_res = np.sum((abs_std - y_fit)**2)
        ss_tot = np.sum((abs_std - np.mean(abs_std))**2)
        r2 = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0.0
    else:
        m, b, r2 = 1.0, 0.0, 0.0
except:
    m, b, r2 = 1.0, 0.0, 0.0

st.sidebar.success(f"Ecuación: $A = {m:.4f}C + {b:.4f}$ | $R^2 = {r2:.4f}$")

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
st.sidebar.header("🧪 3. Registro por Condición")

frutas_disponibles = ["Manzana", "Pera", "Durazno/Nectarina", "Kiwi", "Frutos Rojos", "Otra Fruta"]
fruta_sel = st.sidebar.selectbox("Seleccione la Fruta / Matriz", frutas_disponibles)
agitacion_sel = st.sidebar.selectbox("Condición de Agitación", ["Sin Agitación (0 rpm)", "Con Agitación (200 rpm)"])

condicion_nombre = f"{fruta_sel} - {agitacion_sel}"
st.sidebar.info(f"Registrando triplicado para: **{condicion_nombre}**")

st.sidebar.markdown("Ingrese las absorbancias experimentales para las tres réplicas:")
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
            st.sidebar.error("⚠️ La cantidad de valores de absorbancia debe coincidir exactamente con los tiempos.")
        else:
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

# --- PANTALLA PRINCIPAL ---
st.markdown("---")
st.header("📊 Análisis de Resultados y Curva de Calibrado")

# Mostrar Curva de Calibrado en la parte superior o en pestañas principales
col_c1, col_c2 = st.columns([1, 1])
with col_c1:
    st.subheader("📈 Gráfica de la Curva de Calibrado")
    fig_cal, ax_cal = plt.subplots(figsize=(6, 4))
    ax_cal.scatter(conc_std, abs_std, color="purple", label="Estándares experimentales", zorder=5)
    
    # Línea de tendencia
    x_line = np.linspace(min(conc_std), max(conc_std), 100)
    ax_cal.plot(x_line, m * x_line + b, color="orange", linestyle="--", label=f"A = {m:.4f}C + {b:.4f}\n$R^2$ = {r2:.4f}")
    
    ax_cal.set_xlabel("Concentración")
    ax_cal.set_ylabel("Absorbancia ($A_{600}$)")
    ax_cal.set_title("Curva de Calibración")
    ax_cal.grid(True, linestyle="--", alpha=0.6)
    ax_cal.legend()
    st.pyplot(fig_cal)

with col_c2:
    st.subheader("📝 Parámetros de la Recta")
    st.markdown(
        f"""
        La regresión lineal obtenida a partir de los estándares ingresados permite transformar 
        los valores de absorbancia de las muestras experimentales en **concentraciones** mediante la fórmula despejada:
        
        $$C = \\frac{A - b}{m}$$
        
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
historial = st.session_state.historial

if len(historial) > 0:
    st.markdown("---")
    st.header("📋 Cinética de Extracción por Muestra")
    st.markdown(
        """
        A continuación se muestran las tablas detalladas con los promedios de absorbancia, 
        la desviación estándar muestral ($s$), el coeficiente de variación ($CV\%$), la velocidad aparente 
        y la conversión a concentración utilizando la curva de calibrado.
        """
    )

    datos_procesados = {}
    for item in historial:
        cond = item["Condicion"]
        r1_arr = item["R1"]
        r2_arr = item["R2"]
        r3_arr = item["R3"]

        # Promedio de absorbancia
        a_prom = (r1_arr + r2_arr + r3_arr) / 3.0

        # Desviación estándar muestral
        suma_cuad = (r1_arr - a_prom)**2 + (r2_arr - a_prom)**2 + (r3_arr - a_prom)**2
        s_val = np.sqrt(suma_cuad / 2.0)

        # Coeficiente de variación
        cv_val = np.divide(s_val, a_prom, out=np.zeros_like(s_val), where=a_prom!=0) * 100

        # Concentración promedio usando la curva de calibrado (C = (A - b) / m)
        if m != 0:
            c_prom = (a_prom - b) / m
        else:
            c_prom = np.zeros_like(a_prom)

        # Extracción relativa normalizada
        a_inicial = a_prom[0]
        a_final = a_prom[-1]
        denominador_erel = a_final - a_inicial
        if denominador_erel != 0:
            erel_val = ((a_prom - a_inicial) / denominador_erel) * 100
        else:
            erel_val = np.zeros_like(a_prom)

        # Velocidad aparente de extracción
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
            "CProm": c_prom,
            "S": s_val,
            "CV": cv_val,
            "ERel": erel_val,
            "Velocidades": r_a,
            "IntervalosVel": [f"{int(ti)} a {int(tf)} min" for ti, tf in zip(tiempos[:-1], tiempos[1:])]
        }

    nombres_conds = list(datos_procesados.keys())
    tabs = st.tabs([f"🍇 {c}" for c in nombres_conds] + ["⚡ Análisis de Agitación", "📈 Gráfica Global"])

    # Pestañas individuales por condición
    for idx, cond in enumerate(nombres_conds):
        d = datos_procesados[cond]
        with tabs[idx]:
            st.markdown(f"### Condición evaluada: **{cond}**")
            st.markdown("Desglose de réplicas experimentales, estadística descriptiva y transformación a concentración.")
            
            st.markdown("#### 📊 Tabla Principal: Absorbancias, Promedios y Concentración Calculada")
            df_principal = pd.DataFrame({
                "Tiempo (min)": d["Tiempos"],
                "Réplica 1 ($A_1$)": d["R1"],
                "Réplica 2 ($A_2$)": d["R2"],
                "Réplica 3 ($A_3$)": d["R3"],
                "Promedio ($\overline{A}$)": [f"{v:.4f}" for v in d["AProm"]],
                "Desv. Estándar ($s$)": [f"{v:.4f}" for v in d["S"]],
                "CV (%)": [f"{v:.2f}%" for v in d["CV"]],
                "Concentración ($\overline{C}$)": [f"{v:.4f}" for v in d["CProm"]],
                "Extracción Relativa ($E_{rel}\%$)": [f"{v:.2f}%" for v in d["ERel"]]
            })
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

    # Pestaña de Análisis Comparativo de Agitación
    with tabs[len(nombres_conds)]:
        st.markdown("### ⚡ Efecto de la Agitación (Sin Agitación vs Con Agitación)")
        st.markdown("Evaluación del impacto hidrodinámico comparando los resultados por tipo de muestra vegetal.")

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
            st.warning("⚠️ Para visualizar esta sección, registra al menos una fruta evaluando ambas condiciones de agitación.")

    # Pestaña de Gráfica Global
    with tabs[len(nombres_conds) + 1]:
        st.markdown("### 📈 Gráfica Global de Cinética de Extracción")
        st.markdown("Evolución temporal de la concentración promedio obtenida a través de la curva de calibrado.")
        
        fig, ax = plt.subplots(figsize=(10, 6))
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
        ax.set_title("Cinética de Extracción (Concentración vs Tiempo)", fontsize=14)
        ax.grid(True, linestyle="--", alpha=0.7)
        ax.legend(bbox_to_anchor=(1.05, 1), loc="upper left")
        plt.tight_layout()
        st.pyplot(fig)

else:
    st.info("👈 Ingresa los datos de tu curva de calibrado y guarda al menos una condición en la barra lateral para iniciar el análisis.")
