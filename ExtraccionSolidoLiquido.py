import matplotlib.pyplot as plt
import numpy as np
import streamlit as st
from scipy.stats import linregress

st.set_page_config(
    page_title="Cinética de Extracción Sólido-Líquido", page_icon="🍇", layout="wide"
)

st.title("🍇 Cinética de Extracción y Curva de Calibrado")
st.markdown(
    """
Esta aplicación permite procesar la curva de calibrado espectrofotométrico y analizar las corridas experimentales de extracción sólido-líquido para diferentes tipos de fruta, calculando concentraciones, masa aparente, extracción relativa y velocidades promedio de extracción.
"""
)

# --- INICIALIZAR HISTORIAL EN LA SESIÓN ---
if "HistorialExtraccion" not in st.session_state:
    st.session_state.HistorialExtraccion = []

# --- PARÁMETROS GENERALES Y CALIBRACIÓN ---
st.sidebar.header("⚙️ Parámetros Generales y Calibración")

volumen_agua = st.sidebar.number_input(
    "Volumen de agua (L)", value=1.00, format="%.3f"
)
input_tiempos = st.sidebar.text_area(
    "Tiempos de muestreo (min) (separados por espacio)", "0 5 10 15 20 30"
)

st.sidebar.markdown("---")
st.sidebar.subheader("📈 Datos de Calibrado")
input_conc_e = st.sidebar.text_area(
    "Concentración estándar (g/L)", "0.0 0.5 1.0 1.5 2.0"
)
input_abs_e = st.sidebar.text_area(
    "ABS estándar (600 nm)", "0.00 0.12 0.25 0.38 0.50"
)

# Procesar Calibración de forma dinámica
try:
    tiempo_muestreo = np.array([float(x) for x in input_tiempos.split()])
    conc_e = np.array([float(x) for x in input_conc_e.split()])
    abs_e = np.array([float(x) for x in input_abs_e.split()])

    if len(conc_e) != len(abs_e):
        st.error(
            "⚠️️ La cantidad de valores en Concentración Estándar y ABS Estándar debe ser la misma."
        )
    else:
        # Nota: linregress(x, y). En tu script original pasabas (ABS, Conc) o (Conc, ABS).
        # Verificando tu script: linregress(ABSEstandar, ConcentracionE) -> x=ABS, y=Conc.
        m, b, r, _, _ = linregress(abs_e, conc_e)
        r2 = r**2

        # Mostrar sección de calibración arriba
        col_cal1, col_cal2 = st.columns([1, 1])
        with col_cal1:
            st.subheader("📊 Curva de Calibrado Espectrofotométrico")
            st.write(
                f"- **Pendiente ($m$):** `{m:.4f}` | **Intercepto ($b$):** `{b:.4f}` | **R²:** `{r2:.4f}`"
            )

            fig_cal, ax_cal = plt.subplots(figsize=(6, 3.5))
            ax_cal.plot(conc_e, abs_e, "bo-", label="Estándares")
            ax_cal.set_xlabel("Concentración (g/L)")
            ax_cal.set_ylabel("ABS 600 (nm)")
            ax_cal.set_title("Calibración: Concentración vs ABS")
            ax_cal.grid(True)
            st.pyplot(fig_cal)

except Exception as e:
    st.error(f"Error en los datos de calibración: {e}")

# --- INGRESO DE DATOS EXPERIMENTALES (POR CADA FRUTA) ---
st.sidebar.markdown("---")
st.sidebar.header("🧪 Registro Experimental por Fruta")

fruta = st.sidebar.text_input("Tipo de fruta", "Manzana")
input_abs_exp = st.sidebar.text_area(
    "ABS experimental (600 nm) (separados por espacio)", "0.05 0.15 0.22 0.28 0.31 0.33"
)
concentracion_ref = st.sidebar.number_input(
    "Concentración de referencia (g/L)", value=2.50, format="%.2f"
)

col_b1, col_b2 = st.sidebar.columns(2)
guardar_fruta = col_b1.button("💾 Guardar Fruta")
limpiar_historial = col_b2.button("🗑️ Limpiar Todo")

if limpiar_historial:
    st.session_state.HistorialExtraccion = []
    st.success("Historial de extracciones reiniciado.")

if guardar_fruta:
    try:
        abs_exp = np.array([float(x) for x in input_abs_exp.split()])

        if len(abs_exp) != len(tiempo_muestreo):
            st.sidebar.error(
                "⚠️ La cantidad de valores de ABS experimental debe coincidir con la cantidad de Tiempos de muestreo."
            )
        else:
            # Cálculos principales
            concentracion = (abs_exp - b) / m
            tm = np.diff(tiempo_muestreo)
            c_diff = np.diff(concentracion)
            masa_aparente = concentracion * volumen_agua
            velocidad_promedio = c_diff / tm if np.all(tm > 0) else np.zeros_like(c_diff)
            extraccion_relativa = (
                (concentracion / concentracion_ref) * 100
                if concentracion_ref > 0
                else np.zeros_like(concentracion)
            )

            # Guardar en el historial de sesión
            st.session_state.HistorialExtraccion.append(
                {
                    "Fruta": fruta,
                    "ABSExperimental": abs_exp,
                    "Concentracion": concentracion,
                    "MasaAparente": masa_aparente,
                    "ExtraccionRelativa": extraccion_relativa,
                    "VelocidadPromedio": velocidad_promedio,
                }
            )
            st.sidebar.success(
                f"✅ Datos para **{fruta}** guardados correctamente."
            )
    except Exception as e:
        st.sidebar.error(f"Error procesando datos experimentales: {e}")

# --- MOSTRAR RESULTADOS Y COMPARATIVAS GLOBALES ---
historial = st.session_state.HistorialExtraccion

if len(historial) > 0:
    st.markdown("---")
    st.subheader(
        f"📋 Resultados y Tablas Experimentales ({len(historial)} muestras registradas)"
    )

    # Pestañas para cada fruta individual y comparativas globales
    nombres_frutas = [item["Fruta"] for item in historial]
    tabs = st.tabs(
        [f"🍎 {f}" for f in nombres_frutas]
        + ["📊 Gráfica Global Concentración", "⚡ Velocidades Promedio"]
    )

    # Pestañas individuales para cada fruta
    for idx, item in enumerate(historial):
        with tabs[idx]:
            st.write(f"### Registro Experimental para: **{item['Fruta']}**")

            # Tabla 1: Datos experimentales y transformados
            tabla_1 = {
                "Tiempo (min)": tiempo_muestreo,
                "ABS 600 nm": item["ABSExperimental"],
                "Concentración (g/L)": [f"{val:.2f}" for val in item["Concentracion"]],
                "Masa Aparente (g)": [f"{val:.2f}" for val in item["MasaAparente"]],
                "Extracción Relativa (%)": [
                    f"{val:.2f}" for val in item["ExtraccionRelativa"]
                ],
            }
            st.dataframe(tabla_1, use_container_width=True)

            st.write("### Tabla 2: Velocidad Promedio de Extracción")
            if len(tiempo_muestreo) > 1:
                tabla_2_datos = []
                for ti, tf, vm in zip(
                    tiempo_muestreo[:-1],
                    tiempo_muestreo[1:],
                    item["VelocidadPromedio"],
                ):
                    tabla_2_datos.append(
                        {
                            "Intervalo de tiempo (min)": f"{int(ti)} a {int(tf)}",
                            "Velocidad promedio ((g/L)/min)": f"{vm:.4f}",
                        }
                    )
                st.dataframe(tabla_2_datos, use_container_width=True)

            # Gráfica individual de concentración vs tiempo
            fig_ind, ax_ind = plt.subplots(figsize=(7, 4))
            ax_ind.plot(
                tiempo_muestreo,
                item["Concentracion"],
                marker="o",
                color="green",
                label=item["Fruta"],
            )
            ax_ind.set_xlabel("Tiempo (min)")
            ax_ind.set_ylabel("Concentración (g/L)")
            ax_ind.set_title(f"Concentración vs Tiempo ({item['Fruta']})")
            ax_ind.grid(True)
            ax_ind.legend()
            st.pyplot(fig_ind)

    # Pestaña de Gráfica Global de Concentración
    with tabs[len(historial)]:
        st.subheader("📈 Comparación Global: Concentración vs Tiempo")
        fig_glob, ax_glob = plt.subplots(figsize=(8, 5))
        for item in historial:
            ax_glob.plot(
                tiempo_muestreo,
                item["Concentracion"],
                marker="o",
                label=item["Fruta"],
            )
        ax_glob.set_xlabel("Tiempo (min)")
        ax_glob.set_ylabel("Concentración (g/L)")
        ax_glob.set_title("Cinética de Extracción de Azúcares Reductores")
        ax_glob.grid(True)
        ax_glob.legend()
        st.pyplot(fig_glob)

    # Pestaña de Velocidades Promedio (Gráfico de Barras)
    with tabs[len(historial) + 1]:
        st.subheader(
            "⚡ Comparación de Velocidad Promedio de Extracción por Intervalos"
        )
        if len(tiempo_muestreo) > 1:
            num_intervalos = len(tiempo_muestreo) - 1
            x = np.arange(num_intervalos)
            ancho = 0.2

            fig_bar, ax_bar = plt.subplots(figsize=(9, 5))
            for i, item in enumerate(historial):
                v_prom = item["VelocidadPromedio"]
                ax_bar.bar(
                    x + (i * ancho),
                    v_prom,
                    width=ancho,
                    label=item["Fruta"],
                )

            labels_intervalos = [
                f"{int(tiempo_muestreo[j])}-{int(tiempo_muestreo[j+1])} min"
                for j in range(num_intervalos)
            ]
            ax_bar.set_xlabel("Intervalos de Tiempo")
            ax_bar.set_ylabel("Velocidad Promedio ((g/L) / min)")
            ax_bar.set_title("Velocidad Promedio de Extracción por Intervalos")
            ax_bar.set_xticks(x + ancho * (len(historial) - 1) / 2)
            ax_bar.set_xticklabels(labels_intervalos)
            ax_bar.grid(True, axis="y")
            ax_bar.legend()
            st.pyplot(fig_bar)
else:
    st.info(
        "👈 Ingresa los parámetros de calibración y registra al menos una fruta en la barra lateral para ver los resultados y gráficos."
    )