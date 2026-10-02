import matplotlib.pyplot as plt
import numpy as np
import streamlit as st
from scipy.stats import linregress

st.set_page_config(
    page_title="Calculadora de Filtración a Presión Constante",
    page_icon="🧪",
    layout="wide",
)

st.title("🧪 Laboratorio de Filtración a Presión Constante y Compresibilidad")
st.markdown(
    """
Esta aplicación permite registrar múltiples corridas experimentales a distintas presiones, calcular la resistencia específica de la torta ($\alpha$), la resistencia del medio filtrante ($R_m$), las curvas de caudal y el **coeficiente de compresibilidad ($s$)**.
"""
)

# --- INICIALIZAR HISTORIAL EN LA SESIÓN ---
if "Historial1" not in st.session_state:
    st.session_state.Historial1 = []

# --- ENTRADA DE DATOS EN LA BARRA LATERAL ---
st.sidebar.header("📥 Ingreso de Datos por Corrida")

presion_psi = st.sidebar.number_input(
    "Presión de operación (psi)", value=15.0, format="%.2f"
)
input_tiempo = st.sidebar.text_area(
    "Tiempos (s) (separados por espacio)", "0 30 60 90 120 150"
)
input_peso = st.sidebar.text_area(
    "Pesos de filtrado (kg) (separados por espacio)", "0 0.1 0.25 0.4 0.6 0.85"
)

st.sidebar.markdown("---")
densidad = st.sidebar.number_input(
    "Densidad del filtrado ($kg/m^3$)", value=1000.0, format="%.2f"
)

# Área con alta precisión de decimales solicitada
area = st.sidebar.number_input(
    "Área de filtración ($m^2$)", value=0.050000, format="%.6f", step=0.000001
)

viscosidad = st.sidebar.number_input(
    "Viscosidad del fluido (Pa·s)", value=0.001000, format="%.6f", step=0.00001
)
masa_seca = st.sidebar.number_input(
    "Masa de filtrado seco (g)", value=50.00, format="%.2f"
)
masa_humeda = st.sidebar.number_input(
    "Masa de filtrado húmedo (g)", value=65.00, format="%.2f"
)

# Botones de control
col_btn1, col_btn2 = st.sidebar.columns(2)
guardar_corrida = col_btn1.button("💾 Guardar Corrida")
limpiar_historial = col_btn2.button("🗑️ Limpiar Todo")

if limpiar_historial:
    st.session_state.Historial1 = []
    st.success("Historial reiniciado.")

# Procesar y guardar corrida actual al hacer clic
if guardar_corrida:
    try:
        tiempo = np.array([float(x) for x in input_tiempo.split()])
        peso = np.array([float(x) for x in input_peso.split()])

        if len(tiempo) != len(peso):
            st.error("⚠️ La cantidad de valores en Tiempo y Peso debe ser igual.")
        elif len(tiempo) > 1:
            volumen = peso / densidad
            volumen_final = volumen[-1]
            masa_seca_kg = masa_seca / 1000.0

            concentracion = masa_seca_kg / volumen_final
            va = volumen / area
            tav = (tiempo * area) / volumen

            m, b = np.polyfit(va, tav, 1)
            tava_ajuste = m * va + b

            regresion = linregress(va, tav)
            r = regresion.rvalue
            R = r**2

            pa = presion_psi * 6895  # Conversión psi a Pa
            alpha = (2 * m * pa) / (concentracion * viscosidad)
            rm = (b * pa) / viscosidad

            var_vol = volumen[-1] - volumen[0]
            var_tiempo = tiempo[-1] - tiempo[0]
            caudal_experimental = (
                var_vol / var_tiempo if var_tiempo > 0 else 0
            )
            flux = caudal_experimental / area
            productividad = volumen[-1] / (area * tiempo[-1])
            relacion_masas = masa_humeda / masa_seca

            # Guardar en el historial de la sesión
            st.session_state.Historial1.append(
                {
                    "Tiempo": tiempo,
                    "Volumen": volumen,
                    "Presión": np.full_like(tiempo, presion_psi),
                    "PresionA": pa,
                    "VA": va,
                    "TAV": tav,
                    "Pendiente": m,
                    "Intercepto": b,
                    "R": R,
                    "Ajuste": tava_ajuste,
                    "Alpha": alpha,
                    "RM": rm,
                    "Concentración": concentracion,
                    "CaudalExperimental": caudal_experimental,
                    "Flux": flux,
                    "Productividad": productividad,
                    "RelaciondeMasas": relacion_masas,
                }
            )
            st.sidebar.success(
                f"✅ Corrida a {presion_psi} psi guardada con éxito."
            )
        else:
            st.sidebar.warning("⚠ Ingresa al menos dos puntos de datos.")
    except Exception as e:
        st.sidebar.error(f"Error procesando datos: {e}")

# --- MOSTRAR ANÁLISIS GLOBAL SI HAY CORRIDAS GUARDADAS ---
Historial1 = st.session_state.Historial1

if len(Historial1) > 0:
    st.markdown("---")
    st.subheader(
        f"📊 Resumen de Corridas Registradas ({len(Historial1)} en total)"
    )

    # Mostrar tabla resumen
    resumen_data = []
    for item in Historial1:
        resumen_data.append(
            {
                "Presión (psi)": item["Presión"][0],
                "Concentración (kg/m³)": f"{item['Concentración']:.2f}",
                "Pendiente": f"{item['Pendiente']:.2f}",
                "Intercepto": f"{item['Intercepto']:.2f}",
                "R²": f"{item['R']:.4f}",
                "Alpha (m/kg)": f"{item['Alpha']:.4e}",
                "Rm (m⁻¹)": f"{item['RM']:.4e}",
            }
        )
    st.dataframe(resumen_data, use_container_width=True)

    # Pestañas con los gráficos
    tab1, tab2, tab3, tab4, tab5 = st.tabs(
        [
            "📈 Curvas Básicas",
            "📉 V/A vs tA/V",
            "🌊 Caudales y Flujos",
            "🔬 Alpha vs Presión",
            "📐 Compresibilidad",
        ]
    )

    with tab1:
        col_g1, col_g2 = st.columns(2)
        with col_g1:
            fig, ax = plt.subplots(figsize=(6, 4))
            for item in Historial1:
                ax.plot(
                    item["Tiempo"],
                    item["Presión"],
                    marker="o",
                    label=f"{item['Presión'][0]} psi",
                )
            ax.set_title("Tiempo vs Presión")
            ax.set_xlabel("Tiempo (s)")
            ax.set_ylabel("Presión (psi)")
            ax.legend()
            ax.grid(True)
            st.pyplot(fig)

        with col_g2:
            fig2, ax2 = plt.subplots(figsize=(6, 4))
            for item in Historial1:
                ax2.plot(
                    item["Tiempo"],
                    item["Volumen"],
                    marker="o",
                    label=f"{item['Presión'][0]} psi",
                )
            ax2.set_title("Tiempo vs Volumen")
            ax2.set_xlabel("Tiempo (s)")
            ax2.set_ylabel("Volumen ($m^3$)")
            ax2.legend()
            ax2.grid(True)
            st.pyplot(fig2)

    with tab2:
        fig3, ax3 = plt.subplots(figsize=(8, 5))
        for item in Historial1:
            vp = item["Presión"][0]
            ax3.plot(item["VA"], item["TAV"], marker="o", label=f"Exp {vp} psi")
            ax3.plot(
                item["VA"], item["Ajuste"], linestyle="--", label=f"Ajuste {vp}"
            )
        ax3.set_title("V/A vs (t·A)/V")
        ax3.set_xlabel("V/A (m)")
        ax3.set_ylabel("t·A/V (s/m)")
        ax3.legend()
        ax3.grid(True)
        st.pyplot(fig3)

    with tab3:
        col_c1, col_c2 = st.columns(2)
        with col_c1:
            fig4, ax4 = plt.subplots(figsize=(6, 4))
            for item in Historial1:
                v, t, p = item["Volumen"], item["Tiempo"], item["Presión"][0]
                vi, ti = np.diff(v), np.diff(t)
                caudal_int = vi / ti
                t_medio = (t[1:] + t[:-1]) / 2
                ax4.plot(t_medio, caudal_int, marker="o", label=f"{p} psi")
            ax4.set_title("Caudal vs Tiempo medio")
            ax4.set_xlabel("Tiempo medio (s)")
            ax4.set_ylabel("Caudal ($m^3/s$)")
            ax4.legend()
            ax4.grid(True)
            st.pyplot(fig4)

        with col_c2:
            fig5, ax5 = plt.subplots(figsize=(6, 4))
            for item in Historial1:
                v, t, p = item["Volumen"], item["Tiempo"], item["Presión"][0]
                vi, ti = np.diff(v), np.diff(t)
                caudal_int = vi / ti
                v_int = v[1:]
                ax5.plot(v_int, caudal_int, marker="o", label=f"{p} psi")
            ax5.set_title("Caudal vs Volumen acumulado")
            ax5.set_xlabel("Volumen acumulado ($m^3$)")
            ax5.set_ylabel("Caudal ($m^3/s$)")
            ax5.legend()
            ax5.grid(True)
            st.pyplot(fig5)

    with tab4:
        p1 = [item["PresionA"] for item in Historial1]
        a1 = [item["Alpha"] for item in Historial1]
        fig6, ax6 = plt.subplots(figsize=(8, 5))
        ax6.plot(p1, a1, marker="o", color="purple", linewidth=2)
        ax6.set_title("Resistencia Específica de la Torta (α) vs Presión")
        ax6.set_xlabel("Presión (Pa)")
        ax6.set_ylabel("α (m/kg)")
        ax6.grid(True)
        st.pyplot(fig6)

    with tab5:
        if len(Historial1) >= 2:
            alpha_arr = np.array([item["Alpha"] for item in Historial1])
            presion_arr = np.array([item["PresionA"] for item in Historial1])

            l_alpha = np.log(alpha_arr)
            l_presion = np.log(presion_arr)

            s, intercepto_alpha = np.polyfit(l_presion, l_alpha, 1)
            alpha_arreglo = s * l_presion + intercepto_alpha

            st.success(
                f"### 🎯 Coeficiente de Compresibilidad ($s$): **{s:.4f}**"
            )

            fig7, ax7 = plt.subplots(figsize=(8, 5))
            ax7.plot(
                l_presion, l_alpha, "bo", label="Datos experimentales (ln)"
            )
            ax7.plot(
                l_presion,
                alpha_arreglo,
                "r--",
                label=f"Ajuste lineal (s = {s:.2f})",
            )
            ax7.set_title("ln(α) vs ln(Presión)")
            ax7.set_xlabel("ln(Presión [Pa])")
            ax7.set_ylabel("ln(α)")
            ax7.legend()
            ax7.grid(True)
            st.pyplot(fig7)
        else:
            st.info(
                "ℹ️ Registra al menos **2 corridas** a diferentes presiones para calcular y graficar el coeficiente de compresibilidad ($s$)."
            )

else:
    st.info(
        "👈 Ingresa los datos en la barra lateral y haz clic en **'Guardar Corrida'** para comenzar el análisis comparativo."
    )
