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
Esta aplicación procesa la curva de calibrado y agrupa automáticamente las réplicas experimentales por tipo de fruta para calcular promedios, desviaciones estándar y velocidades de extracción.
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

# Procesar Calibración
try:
    tiempo_muestreo = np.array([float(x) for x in input_tiempos.split()])
    conc_e = np.array([float(x) for x in input_conc_e.split()])
    abs_e = np.array([float(x) for x in input_abs_e.split()])

    if len(conc_e) != len(abs_e):
        st.error("⚠ La cantidad de valores en Concentración Estándar y ABS Estándar debe ser la misma.")
    else:
        m, b, r, _, _ = linregress(conc_e, abs_e)
        r2 = r**2

        col_cal1, col_cal2 = st.columns([1, 1])
        with col_cal1:
            st.subheader("📊 Curva de Calibrado Espectrofotométrico")
            st.write(f"- **Pendiente ($m$):** `{m:.4f}` | **Intercepto ($b$):** `{b:.4f}` | **R²:** `{r2:.4f}`")

            fig_cal, ax_cal = plt.subplots(figsize=(6, 3.5))
            ax_cal.scatter(conc_e, abs_e, color="blue", label="Estándares")
            line_x = np.linspace(min(conc_e), max(conc_e), 100)
            ax_cal.plot(line_x, m * line_x + b, color="red", label=f"Regresión: y = {m:.4f}x + {b:.4f}")
            ax_cal.set_xlabel("Concentración (g/L)")
            ax_cal.set_ylabel("ABS 600 (nm)")
            ax_cal.set_title("Calibración: Concentración vs ABS")
            ax_cal.grid(True)
            ax_cal.legend()
            st.pyplot(fig_cal)

except Exception as e:
    st.error(f"Error en los datos de calibración: {e}")

# --- INGRESO DE DATOS EXPERIMENTALES (RÉPLICAS) ---
st.sidebar.markdown("---")
st.sidebar.header("🧪 Registro de Réplicas")
st.sidebar.info("💡 Escribe el nombre base de la muestra (ej: 'Manzana') para agrupar automáticamente sus réplicas.")

fruta_nombre = st.sidebar.text_input("Nombre de la muestra / Fruta", "Manzana")
input_abs_exp = st.sidebar.text_area(
    "ABS experimental (600 nm) (separados por espacio)", "0.05 0.15 0.22 0.28 0.31 0.33"
)
concentracion_ref = st.sidebar.number_input(
    "Concentración de referencia (g/L)", value=2.50, format="%.2f"
)

col_b1, col_b2 = st.sidebar.columns(2)
guardar_corrida = col_b1.button("💾 Guardar Réplica")
limpiar_historial = col_b2.button("🗑️ Limpiar Todo")

if limpiar_historial:
    st.session_state.HistorialExtraccion = []
    st.success("Historial reiniciado.")

if guardar_corrida:
    try:
        abs_exp = np.array([float(x) for x in input_abs_exp.split()])

        if len(abs_exp) != len(tiempo_muestreo):
            st.sidebar.error("⚠️ La cantidad de valores de ABS experimental debe coincidir con los Tiempos de muestreo.")
        else:
            concentracion = (abs_exp - b) / m
            masa_aparente = concentracion * volumen_agua
            extraccion_relativa = (
                (concentracion / concentracion_ref) * 100
                if concentracion_ref > 0
                else np.zeros_like(concentracion)
            )

            # Guardar la corrida individual en el historial
            st.session_state.HistorialExtraccion.append(
                {
                    "Grupo": fruta_nombre.strip(),
                    "ABSExperimental": abs_exp,
                    "Concentracion": concentracion,
                    "MasaAparente": masa_aparente,
                    "ExtraccionRelativa": extraccion_relativa,
                }
            )
            st.sidebar.success(f"✅ Réplica guardada bajo el grupo: **{fruta_nombre.strip()}**")
    except Exception as e:
        st.sidebar.error(f"Error procesando datos: {e}")

# --- AGRUPAR Y PROCESAR ESTADÍSTICAS ---
historial = st.session_state.HistorialExtraccion

if len(historial) > 0:
    st.markdown("---")
    st.subheader(f"📋 Resultados y Análisis Estadístico de Réplicas ({len(historial)} corridas totales)")

    # Obtener nombres de grupos únicos (ej: 'Manzana', 'Pera')
    grupos_unicos = sorted(list(set(item["Grupo"] for item in historial)))

    # Pestañas para cada grupo y comparativas globales
    tabs = st.tabs([f"🧪 {g}" for g in grupos_unicos] + ["📊 Gráfica Global con Promedios", "⚡ Velocidades Estadísticas"])

    # Diccionario para almacenar los promedios globales por grupo (para usarlos en comparativas)
    datos_agrupados = {}

    for idx, grupo in enumerate(grupos_unicos):
        # Filtrar todas las corridas que pertenecen a este grupo
        corridas_grupo = [item for item in historial if item["Grupo"] == grupo]
        
        # Extraer matrices de concentración para calcular media y desviación estándar
            # shape: (num_replicas, num_tiempos)
        matriz_conc = np.array([c["Concentracion"] for c in corridas_grupo])
        matriz_masa = np.array([c["MasaAparente"] for c in corridas_grupo])
        matriz_ext = np.array([c["ExtraccionRelativa"] for c in corridas_grupo])

        # Cálculos estadísticos (si hay 1 réplica, SD = 0)
        conc_prom = np.mean(matriz_conc, axis=0)
        conc_std = np.std(matriz_conc, axis=0, ddof=1) if len(corridas_grupo) > 1 else np.zeros_like(conc_prom)

        masa_prom = np.mean(matriz_masa, axis=0)
        ext_prom = np.mean(matriz_ext, axis=0)

        # Guardar resumen del grupo
        datos_agrupados[grupo] = {
            "Tiempos": tiempo_muestreo,
            "ConcProm": conc_prom,
            "ConcStd": conc_std,
            "Corridas": corridas_grupo
        }

        with tabs[idx]:
            st.write(f"### Grupo: **{grupo}** ({len(corridas_grupo)} réplica(s) registrada(s))")

            # Mostrar tabla resumen con Promedio y Desviación Estándar
            tabla_resumen = {
                "Tiempo (min)": tiempo_muestreo,
                "Conc. Promedio (g/L)": [f"{v:.2f}" for v in conc_prom],
                "Desv. Estándar (± SD)": [f"{v:.2f}" for v in conc_std],
                "Masa Aparente Prom. (g)": [f"{v:.2f}" for v in masa_prom],
                "Extracción Relativa Prom. (%)": [f"{v:.2f}" for v in ext_prom],
            }
            st.dataframe(tabla_resumen, use_container_width=True)

            # Gráfica individual del grupo mostrando las réplicas tenues y la línea de promedio con error
            fig_g, ax_g = plt.subplots(figsize=(7, 4))
            for r_idx, c_item in enumerate(corridas_grupo):
                ax_g.plot(tiempo_muestreo, c_item["Concentracion"], linestyle="--", alpha=0.4, label=f"Réplica {r_idx+1}")
            
            # Curva promedio con barras de error
            ax_g.errorbar(tiempo_muestreo, conc_prom, yerr=conc_std, fmt="o-", color="black", linewidth=2, capsize=4, label="Promedio ± SD")
            ax_g.set_xlabel("Tiempo (min)")
            ax_g.set_ylabel("Concentración (g/L)")
            ax_g.set_title(f"Cinética con Réplicas: {grupo}")
            ax_g.grid(True)
            ax_g.legend()
            st.pyplot(fig_g)

    # --- PANEL DE SELECCIÓN GLOBAL ---
    st.markdown("---")
    st.subheader("🎛️ Selector de Grupos para Gráficos Globales")
    
    cols_check = st.columns(min(len(grupos_unicos), 4))
    grupos_seleccionados = []
    
    for idx, grupo in enumerate(grupos_unicos):
        col_idx = idx % len(cols_check)
        with cols_check[col_idx]:
            if st.checkbox(f"Mostrar {grupo}", value=True, key=f"chk_grp_{idx}"):
                grupos_seleccionados.append(grupo)

    # Pestaña de Gráfica Global con Promedios
    with tabs[len(grupos_unicos)]:
        st.subheader("📈 Comparación Global de Promedios (con Barras de Error)")
        if len(grupos_seleccionados) > 0:
            fig_glob, ax_glob = plt.subplots(figsize=(8, 5))
            for grupo in grupos_seleccionados:
                d = datos_agrupados[grupo]
                ax_glob.errorbar(
                    d["Tiempos"],
                    d["ConcProm"],
                    yerr=d["ConcStd"],
                    marker="o",
                    capsize=4,
                    label=grupo,
                )
            ax_glob.set_xlabel("Tiempo (min)")
            ax_glob.set_ylabel("Concentración Promedio (g/L)")
            ax_glob.set_title("Comparativa Cinética de Grupos (Promedio ± SD)")
            ax_glob.grid(True)
            ax_glob.legend()
            st.pyplot(fig_glob)
        else:
            st.warning("⚠️ Selecciona al menos un grupo arriba.")

    # Pestaña de Velocidades Estadísticas
    with tabs[len(grupos_unicos) + 1]:
        st.subheader("⚡ Velocidades Promedio de Extracción por Intervalos")
        if len(tiempo_muestreo) > 1 and len(grupos_seleccionados) > 0:
            num_intervalos = len(tiempo_muestreo) - 1
            x = np.arange(num_intervalos)
            ancho = min(0.2, 0.8 / max(len(grupos_seleccionados), 1))

            fig_bar, ax_bar = plt.subplots(figsize=(9, 5))
            for i, grupo in enumerate(grupos_seleccionados):
                d = datos_agrupados[grupo]
                # Calcular velocidad usando el promedio
                tm = np.diff(d["Tiempos"])
                c_diff = np.diff(d["ConcProm"])
                v_prom = c_diff / tm if np.all(tm > 0) else np.zeros_like(c_diff)

                ax_bar.bar(
                    x + (i * ancho),
                    v_prom,
                    width=ancho,
                    label=grupo,
                )

            labels_intervalos = [
                f"{int(tiempo_muestreo[j])}-{int(tiempo_muestreo[j+1])} min"
                for j in range(num_intervalos)
            ]
            ax_bar.set_xlabel("Intervalos de Tiempo")
            ax_bar.set_ylabel("Velocidad Promedio del Grupo ((g/L) / min)")
            ax_bar.set_title("Velocidades Promedio de Extracción")
            ax_bar.set_xticks(x + ancho * (len(grupos_seleccionados) - 1) / 2)
            ax_bar.set_xticklabels(labels_intervalos)
            ax_bar.grid(True, axis="y")
            ax_bar.legend()
            st.pyplot(fig_bar)
        else:
            st.warning("⚠️ Selecciona al menos un grupo arriba y verifica los tiempos.")
else:
    st.info("👈 Ingresa los datos de calibración y registra tus réplicas en la barra lateral.")
