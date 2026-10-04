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
Esta aplicación procesa la curva de calibrado, administra réplicas experimentales sin errores de tipeo y calcula automáticamente promedios y desviaciones estándar.
"""
)

# --- INICIALIZAR ESTADOS EN LA SESIÓN ---
if "HistorialExtraccion" not in st.session_state:
    st.session_state.HistorialExtraccion = []

if "ListaCondiciones" not in st.session_state:
    # Lista inicial basada en tus 4 frutas con y sin agitación para evitar tipeo manual
    st.session_state.ListaCondiciones = [
        "Manzana - Con Agitación", "Manzana - Sin Agitación",
        "Pera - Con Agitación", "Pera - Sin Agitación",
        "Plátano - Con Agitación", "Plátano - Sin Agitación",
        "Naranja - Con Agitación", "Naranja - Sin Agitación"
    ]

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

# --- INGRESO DE DATOS EXPERIMENTALES (RÉPLICAS CON SELECTOR ANTITIEMPO) ---
st.sidebar.markdown("---")
st.sidebar.header("🧪 Ingreso de Réplicas")
st.sidebar.info("💡 Selecciona la condición para evitar errores de tipeo y agrupar automáticamente las 3 réplicas.")

# Selector para evitar duplicados por errores de tipeo
tipo_ingreso = st.sidebar.radio("Modo de Condición", ["Elegir existente", "Crear nueva condición"])

if tipo_ingreso == "Elegir existente":
    condicion_nombre = st.sidebar.selectbox("Selecciona la Condición", st.session_state.ListaCondiciones)
else:
    nueva_cond = st.sidebar.text_input("Nombre de la nueva condición", "Fruta Nueva - Con Agitación")
    condicion_nombre = nueva_cond.strip()
    if condicion_nombre and condicion_nombre not in st.session_state.ListaCondiciones:
        st.session_state.ListaCondiciones.append(condicion_nombre)

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

            grupo_base = condicion_nombre.strip()
            replicas_existentes = [item for item in st.session_state.HistorialExtraccion if item["Grupo"] == grupo_base]
            num_replica = len(replicas_existentes) + 1

            st.session_state.HistorialExtraccion.append(
                {
                    "Grupo": grupo_base,
                    "ID_Replica": num_replica,
                    "EtiquetaCompleta": f"{grupo_base} (R{num_replica})",
                    "ABSExperimental": abs_exp,
                    "Concentracion": concentracion,
                    "MasaAparente": masa_aparente,
                    "ExtraccionRelativa": extraccion_relativa,
                }
            )
            st.sidebar.success(f"✅ Guardado: **{grupo_base}** (Réplica #{num_replica})")
    except Exception as e:
        st.sidebar.error(f"Error procesando datos: {e}")

# --- AGRUPAR Y PROCESAR ESTADÍSTICAS ---
historial = st.session_state.HistorialExtraccion

if len(historial) > 0:
    st.markdown("---")
    st.subheader(f"📋 Panel de Resultados y Control ({len(historial)} registros totales)")

    # Solo considerar grupos que tengan datos en el historial
    grupos_unicos = sorted(list(set(item["Grupo"] for item in historial)))
    
    datos_agrupados = {}
    for grupo in grupos_unicos:
        corridas_grupo = [item for item in historial if item["Grupo"] == grupo]
        matriz_conc = np.array([c["Concentracion"] for c in corridas_grupo])
        matriz_masa = np.array([c["MasaAparente"] for c in corridas_grupo])
        matriz_ext = np.array([c["ExtraccionRelativa"] for c in corridas_grupo])

        conc_prom = np.mean(matriz_conc, axis=0)
        conc_std = np.std(matriz_conc, axis=0, ddof=1) if len(corridas_grupo) > 1 else np.zeros_like(conc_prom)
        masa_prom = np.mean(matriz_masa, axis=0)
        ext_prom = np.mean(matriz_ext, axis=0)

        tm = np.diff(tiempo_muestreo)
        c_diff = np.diff(conc_prom)
        velocidad_promedio_grupo = c_diff / tm if np.all(tm > 0) else np.zeros_like(c_diff)

        datos_agrupados[grupo] = {
            "Tiempos": tiempo_muestreo,
            "ConcProm": conc_prom,
            "ConcStd": conc_std,
            "MasaProm": masa_prom,
            "ExtProm": ext_prom,
            "VelocidadPromedio": velocidad_promedio_grupo,
            "Corridas": corridas_grupo
        }

    tabs = st.tabs([f"🧪 {g}" for g in grupos_unicos] + ["📊 Tabla Global y Gráficos", "⚡ Velocidades Estadísticas"])

    for idx, grupo in enumerate(grupos_unicos):
        d = datos_agrupados[grupo]
        with tabs[idx]:
            st.write(f"### Condición: **{grupo}** ({len(d['Corridas'])} réplica(s) agrupadas)")

            st.write("#### Resumen Estadístico del Grupo (Promedio Único ± SD)")
            tabla_resumen = {
                "Tiempo (min)": tiempo_muestreo,
                "Conc. Promedio (g/L)": [f"{v:.2f}" for v in d["ConcProm"]],
                "Desv. Estándar (± SD)": [f"{v:.2f}" for v in d["ConcStd"]],
                "Masa Aparente Prom. (g)": [f"{v:.2f}" for v in d["MasaProm"]],
                "Extracción Relativa Prom. (%)": [f"{v:.2f}" for v in d["ExtProm"]],
            }
            st.dataframe(tabla_resumen, use_container_width=True)

            st.write("#### Velocidad Promedio de Extracción por Intervalos")
            if len(tiempo_muestreo) > 1:
                tabla_2_datos = []
                for ti, tf, vm in zip(tiempo_muestreo[:-1], tiempo_muestreo[1:], d["VelocidadPromedio"]):
                    tabla_2_datos.append({
                        "Intervalo de tiempo (min)": f"{int(ti)} a {int(tf)}",
                        "Velocidad promedio ((g/L)/min)": f"{vm:.4f}",
                    })
                st.dataframe(tabla_2_datos, use_container_width=True)

            fig_g, ax_g = plt.subplots(figsize=(7, 4))
            for c_item in d["Corridas"]:
                ax_g.plot(tiempo_muestreo, c_item["Concentracion"], linestyle="--", alpha=0.4, label=f"R{c_item['ID_Replica']}")
            
            ax_g.errorbar(tiempo_muestreo, d["ConcProm"], yerr=d["ConcStd"], fmt="o-", color="black", linewidth=2, capsize=4, label="Promedio Único ± SD")
            ax_g.set_xlabel("Tiempo (min)")
            ax_g.set_ylabel("Concentración (g/L)")
            ax_g.set_title(f"Cinética con Réplicas: {grupo}")
            ax_g.grid(True)
            ax_g.legend()
            st.pyplot(fig_g)

    # --- PANEL DE SELECCIÓN CON CHECKBOXES DIVIDIDO ---
    st.markdown("---")
    st.subheader("🎛️ Panel de Control de Visualización")
    st.markdown("Selecciona qué deseas graficar o comparar sin saturar el gráfico:")

    col_chk1, col_chk2 = st.columns(2)

    with col_chk1:
        st.markdown("##### 🔍 Réplicas Individuales (Opcional)")
        corridas_seleccionadas = []
        for item in historial:
            if st.checkbox(item["EtiquetaCompleta"], value=False, key=f"chk_corrida_{item['EtiquetaCompleta']}"):
                corridas_seleccionadas.append(item)

    with col_chk2:
        st.markdown("##### 📊 Promedios de Grupos (Recomendado)")
        grupos_seleccionados = []
        for grupo in grupos_unicos:
            if st.checkbox(f"Promedio: {grupo}", value=True, key=f"chk_grupo_{grupo}"):
                grupos_seleccionados.append(grupo)

    # Pestaña de Tabla Global y Gráfica Global
    with tabs[len(grupos_unicos)]:
        st.subheader("📋 Tabla Consolidada de Todos los Grupos (Promedios y SD)")
        tabla_global = {"Tiempo (min)": tiempo_muestreo}
        for grupo in grupos_unicos:
            tabla_global[f"{grupo} (Prom. g/L)"] = [f"{v:.2f}" for v in datos_agrupados[grupo]["ConcProm"]]
            tabla_global[f"{grupo} (± SD)"] = [f"{v:.2f}" for v in datos_agrupados[grupo]["ConcStd"]]
        st.dataframe(tabla_global, use_container_width=True)

        st.markdown("---")
        st.subheader("📈 Gráfica Global Comparativa")
        
        if len(grupos_seleccionados) > 0 or len(corridas_seleccionadas) > 0:
            fig_glob, ax_glob = plt.subplots(figsize=(9, 5))
            
            for grupo in grupos_seleccionados:
                d = datos_agrupados[grupo]
                ax_glob.errorbar(
                    d["Tiempos"],
                    d["ConcProm"],
                    yerr=d["ConcStd"],
                    marker="o",
                    capsize=4,
                    linewidth=2,
                    label=f"Promedio: {grupo}",
                )

            for c_item in corridas_seleccionadas:
                ax_glob.plot(
                    tiempo_muestreo,
                    c_item["Concentracion"],
                    linestyle=":",
                    alpha=0.6,
                    marker="x",
                    label=f"Réplica: {c_item['EtiquetaCompleta']}"
                )

            ax_glob.set_xlabel("Tiempo (min)")
            ax_glob.set_ylabel("Concentración (g/L)")
            ax_glob.set_title("Comparativa Global de Cinética de Extracción")
            ax_glob.grid(True)
            ax_glob.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
            plt.tight_layout()
            st.pyplot(fig_glob)
        else:
            st.warning("⚠️ Selecciona al menos un grupo o réplica en el panel de checkboxes superior.")

    # Pestaña de Velocidades Estadísticas Globales
    with tabs[len(grupos_unicos) + 1]:
        st.subheader("⚡ Comparación de Velocidades Promedio por Grupos")
        if len(tiempo_muestreo) > 1 and len(grupos_seleccionados) > 0:
            num_intervalos = len(tiempo_muestreo) - 1
            x = np.arange(num_intervalos)
            ancho = min(0.2, 0.8 / max(len(grupos_seleccionados), 1))

            fig_bar, ax_bar = plt.subplots(figsize=(9, 5))
            for i, grupo in enumerate(grupos_seleccionados):
                d = datos_agrupados[grupo]
                ax_bar.bar(
                    x + (i * ancho),
                    d["VelocidadPromedio"],
                    width=ancho,
                    label=grupo,
                )

            labels_intervalos = [
                f"{int(tiempo_muestreo[j])}-{int(tiempo_muestreo[j+1])} min"
                for j in range(num_intervalos)
            ]
            ax_bar.set_xlabel("Intervalos de Tiempo")
            ax_bar.set_ylabel("Velocidad Promedio del Grupo ((g/L) / min)")
            ax_bar.set_title("Velocidades Promedio de Extracción por Grupos")
            ax_bar.set_xticks(x + ancho * (len(grupos_seleccionados) - 1) / 2)
            ax_bar.set_xticklabels(labels_intervalos)
            ax_bar.grid(True, axis="y")
            ax_bar.legend()
            st.pyplot(fig_bar)
        else:
            st.warning("⚠️ Selecciona al menos un grupo (promedio) en el panel de checkboxes.")
else:
    st.info("👈 Ingresa los datos de calibración y registra tus réplicas en la barra lateral.")
