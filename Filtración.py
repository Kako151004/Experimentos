import matplotlib.pyplot as plt
import numpy as np
import streamlit as st

st.set_page_config(
    page_title="Calculadora de Filtración a Presión Constante",
    page_icon="🧪",
    layout="wide",
)

st.title("🧪 Laboratorio de Filtración a Presión Constante")
st.markdown(
    """
Esta aplicación permite analizar los datos experimentales de filtración, calcular la resistencia específica de la torta ($\alpha$), la resistencia del medio filtrante ($R_m$), y generar todas las curvas de rendimiento y compresibilidad con alta precisión.
"""
)

# --- ENTRADA DE DATOS EN LA BARRA LATERAL ---
st.sidebar.header("📥 Parámetros de Operación")

# Entradas para listas de datos (separados por espacios)
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

# Entradas mejoradas con alta precisión en decimales
area = st.sidebar.number_input(
    "Área de filtración ($m^2$)", value=0.0500, format="%.4f", step=0.0001
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
presion_psi = st.sidebar.number_input(
    "Presión de operación (psi)", value=15.0, format="%.2f"
)

# Procesamiento de arreglos y cálculos
try:
    tiempo = np.array([float(x) for x in input_tiempo.split()])
    peso = np.array([float(x) for x in input_peso.split()])

    if len(tiempo) != len(peso):
        st.error(
            "⚠️ La cantidad de valores en Tiempo y Peso debe ser exactamente la misma."
        )
    elif len(tiempo) > 1:
        volumen = peso / densidad
        volumen_final = volumen[-1]
        masa_seca_kg = masa_seca / 1000.0
        masa_humeda_kg = masa_humeda / 1000.0

        concentracion = masa_seca_kg / volumen_final
        va = volumen / area
        tav = (tiempo * area) / volumen

        m, b = np.polyfit(va, tav, 1)
        tava_ajuste = m * va + b

        # Regresión para Coeficiente de Determinación R^2
        coeffs = np.polyfit(va, tav, 1)
        p_val = np.poly1d(coeffs)
        y_hat = p_val(va)
        y_bar = np.mean(tav)
        r2 = 1 - np.sum((tav - y_hat) ** 2) / np.sum((tav - y_bar) ** 2)

        pa = presion_psi * 6895  # Conversión de psi a Pa
        alpha = (2 * m * pa) / (concentracion * viscosidad)
        rm = (b * pa) / viscosidad

        # Análisis complementario
        var_vol = volumen[-1] - volumen[0]
        var_tiempo = tiempo[-1] - tiempo[0]
        caudal_experimental = var_vol / var_tiempo if var_tiempo > 0 else 0
        flux = caudal_experimental / area
        productividad = volumen[-1] / (area * tiempo[-1])
        relacion_masas = masa_humeda / masa_seca

        # --- MOSTRAR RESULTADOS EN PANTALLA ---
        st.subheader("📊 Resultados Generales")

        col1, col2, col3 = st.columns(3)
        col1.metric("Resistencia Torta (α)", f"{alpha:.4e} m/kg")
        col2.metric("Resistencia Medio (Rm)", f"{rm:.4e} m⁻¹")
        col3.metric("Coeficiente $R^2$", f"{r2:.6f}")

        # Pestañas organizadas
        tab1, tab2, tab3 = st.tabs(
            ["📋 Tablas de Datos", "📈 Gráficos de Análisis", "📉 Caudal y Flujo"]
        )

        with tab1:
            st.write("### Tabla 1: Datos Experimentales y Transformados")
            data_tabla = {
                "Tiempo (s)": tiempo,
                "Peso (kg)": peso,
                "Volumen (m³)": volumen,
                "V/A (m)": va,
                "t·A/V (s/m)": tav,
            }
            st.dataframe(data_tabla)

            st.write("### Tabla 2: Parámetros Complementarios")
            st.write(
                f"- **Caudal experimental:** {caudal_experimental:.4e} m³/s"
            )
            st.write(f"- **Flux:** {flux:.4e} m/s")
            st.write(f"- **Productividad final:** {productividad:.4f} m/s")
            st.write(
                f"- **Relación masa húmeda/seca:** {relacion_masas:.4f}"
            )

        with tab2:
            st.write("### Gráfico: V/A vs (t·A)/V")
            fig, ax = plt.subplots(figsize=(8, 5))
            ax.plot(va, tav, "bo", label="Datos experimentales")
            ax.plot(va, tava_ajuste, "r--", label=f"Ajuste lineal (R²={r2:.4f})")
            ax.set_xlabel("V/A (m)")
            ax.set_ylabel("t·A/V (s/m)")
            ax.set_title("Gráfico de Filtración a Presión Constante")
            ax.legend()
            ax.grid(True)
            st.pyplot(fig)

            st.write("### Gráfico: Tiempo vs Volumen")
            fig2, ax2 = plt.subplots(figsize=(8, 5))
            ax2.plot(tiempo, volumen, "go-", label=f"Presión {presion_psi} psi")
            ax2.set_xlabel("Tiempo (s)")
            ax2.set_ylabel("Volumen ($m^3$)")
            ax2.set_title("Tiempo vs Volumen Filtrado")
            ax2.legend()
            ax2.grid(True)
            st.pyplot(fig2)

        with tab3:
            st.write("### Gráficos de Caudal en Intervalos")
            if len(tiempo) > 2:
                vi = np.diff(volumen)
                ti = np.diff(tiempo)
                caudal_intervalo = vi / ti
                tiempo_medio = (tiempo[1:] + tiempo[:-1]) / 2
                volumen_intervalo = volumen[1:]

                fig3, ax3 = plt.subplots(figsize=(8, 4))
                ax3.plot(
                    tiempo_medio, caudal_intervalo, "mo-", label="Caudal"
                )
                ax3.set_xlabel("Tiempo medio (s)")
                ax3.set_ylabel("Caudal ($m^3/s$)")
                ax3.set_title("Caudal experimental vs Tiempo medio")
                ax3.grid(True)
                st.pyplot(fig3)

                fig4, ax4 = plt.subplots(figsize=(8, 4))
                ax4.plot(
                    volumen_intervalo,
                    caudal_intervalo,
                    "co-",
                    label="Caudal",
                )
                ax4.set_xlabel("Volumen acumulado ($m^3$)")
                ax4.set_ylabel("Caudal ($m^3/s$)")
                ax4.set_title("Caudal experimental vs Volumen acumulado")
                ax4.grid(True)
                st.pyplot(fig4)

    else:
        st.warning(
            "⚠ Por favor ingresa al menos dos puntos de tiempo y peso para realizar los cálculos."
        )

except Exception as e:
    st.error(f"Error en los datos de entrada o formato. Detalle: {e}")
