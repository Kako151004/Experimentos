import tempfile
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import linregress
from fpdf import FPDF
import streamlit as st

st.set_page_config(
    page_title="Cinética de Extracción Sólido-Líquido", page_icon="🍇", layout="wide"
)

# --- FUNCIÓN PARA GENERAR EL PDF COMPLETO (Incluye Nuevas Gráficas) ---
def generar_pdf_informe(datos_agrupados, m, b, r2, volumen_agua, masa_fruta, efecto_agitacion_datos, tiempo_muestreo, frutas_base):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "Informe Completo - Cinetica de Extraccion Solido-Liquido", ln=True, align="C")
    pdf.ln(2)
    
    # 1. Parámetros Generales
    pdf.set_font("Arial", "B", 10)
    pdf.cell(0, 6, "1. Parametros Generales y Calibracion:", ln=True)
    pdf.set_font("Arial", "", 9)
    pdf.cell(0, 5, f"- Volumen de agua: {volumen_agua:.3f} L | Masa de fruta: {masa_fruta:.2f} g", ln=True)
    pdf.cell(0, 5, f"- Curva de Calibrado: y = {m:.4f}x + {b:.4f}  (R2 = {r2:.4f})", ln=True)
    pdf.ln(4)
    
    # 2. Resultados por Condición
    pdf.set_font("Arial", "B", 10)
    pdf.cell(0, 6, "2. Resultados Estadisticos por Condicion:", ln=True)
    
    for grupo, d in datos_agrupados.items():
        pdf.set_font("Arial", "B", 9)
        pdf.cell(0, 5, f" Condicion: {grupo} ({len(d['Corridas'])} replicas)", ln=True)
        
        pdf.set_font("Arial", "B", 8)
        pdf.cell(12, 5, "T(min)", 1, 0, "C")
        pdf.cell(24, 5, "Conc.(g/L)", 1, 0, "C")
        pdf.cell(18, 5, "SD (±)", 1, 0, "C")
        pdf.cell(18, 5, "CV (%)", 1, 0, "C")
        pdf.cell(24, 5, "Masa Ext.(g)", 1, 0, "C")
        pdf.cell(25, 5, "Ext.Corr(%)", 1, 0, "C")
        pdf.cell(24, 5, "Rend.(%)", 1, 1, "C")
        
        pdf.set_font("Arial", "", 8)
        for i, t in enumerate(d["Tiempos"]):
            pdf.cell(12, 5, f"{t}", 1, 0, "C")
            pdf.cell(24, 5, f"{d['ConcProm'][i]:.2f}", 1, 0, "C")
            pdf.cell(18, 5, f"{d['ConcStd'][i]:.2f}", 1, 0, "C")
            pdf.cell(18, 5, f"{d['CV'][i]:.1f}%", 1, 0, "C")
            pdf.cell(24, 5, f"{d['MasaProm'][i]:.2f}", 1, 0, "C")
            pdf.cell(25, 5, f"{d['ExtProm'][i]:.1f}%", 1, 0, "C")
            pdf.cell(24, 5, f"{d['RendProm'][i]:.2f}%", 1, 1, "C")
        pdf.ln(3)

    # 3. Velocidades Promedio por Intervalos y Gráfico de Barras
    if len(tiempo_muestreo) > 1:
        pdf.add_page()
        pdf.set_font("Arial", "B", 10)
        pdf.cell(0, 6, "3. Velocidades Promedio de Extraccion por Intervalos:", ln=True)
        for grupo, d in datos_agrupados.items():
            pdf.set_font("Arial", "B", 9)
            pdf.cell(0, 5, f" Condicion: {grupo}", ln=True)
            
            pdf.set_font("Arial", "B", 8)
            pdf.cell(50, 5, "Intervalo de tiempo (min)", 1, 0, "C")
            pdf.cell(70, 5, "Velocidad promedio ((g/L)/min)", 1, 1, "C")
            
            pdf.set_font("Arial", "", 8)
            for ti, tf, vm in zip(tiempo_muestreo[:-1], tiempo_muestreo[1:], d["VelocidadPromedio"]):
                pdf.cell(50, 5, f"{int(ti)} a {int(tf)}", 1, 0, "C")
                pdf.cell(70, 5, f"{vm:.4f}", 1, 1, "C")
            pdf.ln(2)

        # Gráfico de barras de velocidades
        pdf.ln(2)
        pdf.set_font("Arial", "B", 10)
        pdf.cell(0, 6, "Grafico de Velocidades Promedio:", ln=True)
        pdf.ln(1)

        num_intervalos = len(tiempo_muestreo) - 1
        x = np.arange(num_intervalos)
        ancho = min(0.2, 0.8 / max(len(datos_agrupados), 1))

        fig_bar_temp, ax_bar_temp = plt.subplots(figsize=(7, 3.5))
        for i, (grupo, d) in enumerate(datos_agrupados.items()):
            ax_bar_temp.bar(
                x + (i * ancho),
                d["VelocidadPromedio"],
                width=ancho,
                label=grupo,
            )

        labels_intervalos = [
            f"{int(tiempo_muestreo[j])}-{int(tiempo_muestreo[j+1])}m"
            for j in range(num_intervalos)
        ]
        ax_bar_temp.set_xlabel("Intervalos de Tiempo")
        ax_bar_temp.set_ylabel("Velocidad ((g/L)/min)")
        ax_bar_temp.set_title("Velocidades Promedio de Extraccion")
        ax_bar_temp.set_xticks(x + ancho * (len(datos_agrupados) - 1) / 2)
        ax_bar_temp.set_xticklabels(labels_intervalos, fontsize=8)
        ax_bar_temp.grid(True, axis="y")
        ax_bar_temp.legend(fontsize=7)
        
        img_bar_tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
        plt.savefig(img_bar_tmp.name, bbox_inches="tight", dpi=150)
        plt.close(fig_bar_temp)
        
        pdf.image(img_bar_tmp.name, x=15, y=pdf.get_y() + 2, w=180)
        pdf.ln(5)
        
    # 4. Análisis de Efecto de Agitación (Tabla y Gráfico Dinámico vs Tiempo)
    if len(efecto_agitacion_datos) > 0:
        pdf.add_page()
        pdf.set_font("Arial", "B", 10)
        pdf.cell(0, 6, "4. Analisis del Efecto de la Agitacion:", ln=True)
        
        pdf.set_font("Arial", "B", 8)
        pdf.cell(45, 5, "Matriz / Fruta", 1, 0, "C")
        pdf.cell(35, 5, "Conc. Con Agit.", 1, 0, "C")
        pdf.cell(35, 5, "Conc. Sin Agit.", 1, 0, "C")
        pdf.cell(35, 5, "Dif. Absoluta", 1, 0, "C")
        pdf.cell(30, 5, "Efecto (%)", 1, 1, "C")
        
        pdf.set_font("Arial", "", 8)
        for ef in efecto_agitacion_datos:
            pdf.cell(45, 5, f"{ef['Matriz / Fruta']}", 1, 0, "L")
            pdf.cell(35, 5, f"{ef['Conc. Final Con Agit. (g/L)']}", 1, 0, "C")
            pdf.cell(35, 5, f"{ef['Conc. Final Sin Agit. (g/L)']}", 1, 0, "C")
            pdf.cell(35, 5, f"{ef['Diferencia Absoluta (g/L)']}", 1, 0, "C")
            pdf.cell(30, 5, f"{ef['Efecto Porcentual Agitación (%)']}", 1, 1, "C")
        pdf.ln(4)

        # Gráfico: Efecto Porcentual de Agitación (%) vs Tiempo
        pdf.set_font("Arial", "B", 10)
        pdf.cell(0, 6, "Efecto Porcentual de Agitacion (%) vs Tiempo:", ln=True)
        pdf.ln(1)

        fig_ef_temp, ax_ef_temp = plt.subplots(figsize=(7, 3.5))
        for fruta in frutas_base:
            cond_con = f"{fruta} - Con Agitación"
            cond_sin = f"{fruta} - Sin Agitación"
            if cond_con in datos_agrupados and cond_sin in datos_agrupados:
                c_con = datos_agrupados[cond_con]["ConcProm"]
                c_sin = datos_agrupados[cond_sin]["ConcProm"]
                # Evitar división por cero
                efecto_t = np.where(c_sin > 0, ((c_con - c_sin) / c_sin) * 100, 0.0)
                ax_ef_temp.plot(tiempo_muestreo, efecto_t, marker="o", label=fruta)

        ax_ef_temp.set_xlabel("Tiempo (min)")
        ax_ef_temp.set_ylabel("Efecto de Agitación (%)")
        ax_ef_temp.set_title("Evolución Temporal del Efecto de Agitación")
        ax_ef_temp.grid(True)
        ax_ef_temp.legend(fontsize=7)

        img_ef_tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
        plt.savefig(img_ef_tmp.name, bbox_inches="tight", dpi=150)
        plt.close(fig_ef_temp)

        pdf.image(img_ef_tmp.name, x=15, y=pdf.get_y() + 2, w=180)
        pdf.ln(5)

    # 5. Gráfico de Extracción Relativa Corregida (Erel %) vs Tiempo
    pdf.add_page()
    pdf.set_font("Arial", "B", 10)
    pdf.cell(0, 6, "5. Extraccion Relativa Corregida (Erel %) vs Tiempo:", ln=True)
    pdf.ln(2)

    fig_er_temp, ax_er_temp = plt.subplots(figsize=(7, 3.8))
    for grupo, d in datos_agrupados.items():
        ax_er_temp.plot(tiempo_muestreo, d["ExtProm"], marker="o", label=grupo)
    ax_er_temp.set_xlabel("Tiempo (min)")
    ax_er_temp.set_ylabel("Extracción Relativa Corregida Erel (%)")
    ax_er_temp.set_title("Cinética de Extracción Relativa Normalizada")
    ax_er_temp.grid(True)
    ax_er_temp.legend(fontsize=7, bbox_to_anchor=(1.05, 1), loc='upper left')

    img_er_tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
    plt.savefig(img_er_tmp.name, bbox_inches="tight", dpi=150)
    plt.close(fig_er_temp)

    pdf.image(img_er_tmp.name, x=15, y=pdf.get_y() + 2, w=170)
    pdf.ln(5)

    # 6. Incluir Gráfica Global en el PDF
    pdf.add_page()
    pdf.set_font("Arial", "B", 10)
    pdf.cell(0, 6, "6. Grafica Comparativa Global:", ln=True)
    pdf.ln(2)
    
    fig_temp, ax_temp = plt.subplots(figsize=(7, 4))
    for grupo, d in datos_agrupados.items():
        ax_temp.errorbar(d["Tiempos"], d["ConcProm"], yerr=d["ConcStd"], marker="o", capsize=3, label=grupo)
    ax_temp.set_xlabel("Tiempo (min)")
    ax_temp.set_ylabel("Concentracion (g/L)")
    ax_temp.set_title("Cinetica de Extraccion Global")
    ax_temp.grid(True)
    ax_temp.legend(fontsize=7)
    
    img_tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
    plt.savefig(img_tmp.name, bbox_inches="tight", dpi=150)
    plt.close(fig_temp)
    
    pdf.image(img_tmp.name, x=15, y=pdf.get_y() + 2, w=180)
    
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    pdf.output(tmp.name)
    return tmp.name


st.title("🍇 Cinética de Extracción y Curva de Calibrado")
st.markdown(
    """
Esta aplicación procesa la curva de calibrado, administra réplicas experimentales y permite exportar un informe completo en PDF con un solo clic.
"""
)

# --- INICIALIZAR ESTADOS EN LA SESIÓN ---
if "HistorialExtraccion" not in st.session_state:
    st.session_state.HistorialExtraccion = []

if "ListaCondiciones" not in st.session_state:
    st.session_state.ListaCondiciones = [
        "Manzana - Con Agitación", "Manzana - Sin Agitación",
        "Pera - Con Agitación", "Pera - Sin Agitación",
        "Plátano - Con Agitación", "Plátano - Sin Agitación",
        "Naranja - Con Agitación", "Naranja - Sin Agitación"
    ]

# --- PARÁMETROS GENERALES Y CALIBRACIÓN ---
st.sidebar.header("⚙ Parámetros Generales y Calibración")

volumen_agua = st.sidebar.number_input(
    "Volumen de agua (L)", value=1.00, format="%.3f"
)
masa_fruta = st.sidebar.number_input(
    "Masa de la muestra vegetal (g)", value=50.00, format="%.2f"
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
        st.error("⚠️ La cantidad de valores en Concentración Estándar y ABS Estándar debe ser la misma.")
    else:
        m, b, r, _, _ = linregress(conc_e, abs_e)
        r2 = r**2

        col_cal1, col_cal2 = st.columns([1, 1])
        with col_cal1:
            st.subheader("📊 Curva de Calibrado Espectrofotométrico")
            st.write(f"- **Pendiente (m):** `{m:.4f}` | **Intercepto (b):** `{b:.4f}` | **R²:** `{r2:.4f}`")

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

# --- INGRESO DE DATOS EXPERIMENTALES ---
st.sidebar.markdown("---")
st.sidebar.header("🧪 Ingreso de Réplicas")
tipo_ingreso = st.sidebar.radio("Modo de Condición", ["Elegir existente", "Crear nueva condición"])

if tipo_ingreso == "Elegir existente":
    condicion_base = st.sidebar.selectbox("Selecciona la Condición Base", st.session_state.ListaCondiciones)
    condicion_nombre = condicion_base
else:
    fruta_nueva = st.sidebar.text_input("Nombre de la nueva fruta o matriz", "Zanahoria")
    agitacion_nueva = st.sidebar.selectbox("Condición de agitación", ["Con Agitación", "Sin Agitación"])
    condicion_nombre = f"{fruta_nueva.strip()} - {agitacion_nueva}"
    
    if condicion_nombre and condicion_nombre not in st.session_state.ListaCondiciones:
        st.session_state.ListaCondiciones.append(condicion_nombre)

input_abs_exp = st.sidebar.text_area(
    "ABS experimental (600 nm) (separados por espacio)", "0.05 0.15 0.22 0.28 0.31 0.33"
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
            
            c_ultimo = concentracion[-1] if len(concentracion) > 0 and concentracion[-1] > 0 else 1.0
            extraccion_relativa = (concentracion / c_ultimo) * 100
            rendimiento_aparente = (masa_aparente / masa_fruta) * 100 if masa_fruta > 0 else np.zeros_like(masa_aparente)

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
                    "RendimientoAparente": rendimiento_aparente,
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

    grupos_unicos = sorted(list(set(item["Grupo"] for item in historial)))
    frutas_base = sorted(list(set([g.split(" - ")[0] for g in grupos_unicos if " - " in g])))
    
    datos_agrupados = {}
    for grupo in grupos_unicos:
        corridas_grupo = [item for item in historial if item["Grupo"] == grupo]
        matriz_conc = np.array([c["Concentracion"] for c in corridas_grupo])
        matriz_masa = np.array([c["MasaAparente"] for c in corridas_grupo])
        matriz_ext = np.array([c["ExtraccionRelativa"] for c in corridas_grupo])
        matriz_rend = np.array([c["RendimientoAparente"] for c in corridas_grupo])

        conc_prom = np.mean(matriz_conc, axis=0)
        conc_std = np.std(matriz_conc, axis=0, ddof=1) if len(corridas_grupo) > 1 else np.zeros_like(conc_prom)
        cv_opcional = np.where(conc_prom > 0, (conc_std / conc_prom) * 100, 0.0)

        masa_prom = np.mean(matriz_masa, axis=0)
        ext_prom = np.mean(matriz_ext, axis=0)
        rend_prom = np.mean(matriz_rend, axis=0)

        tm = np.diff(tiempo_muestreo)
        c_diff = np.diff(conc_prom)
        velocidad_promedio_grupo = c_diff / tm if np.all(tm > 0) else np.zeros_like(c_diff)

        datos_agrupados[grupo] = {
            "Tiempos": tiempo_muestreo,
            "ConcProm": conc_prom,
            "ConcStd": conc_std,
            "CV": cv_opcional,
            "MasaProm": masa_prom,
            "ExtProm": ext_prom,
            "RendProm": rend_prom,
            "VelocidadPromedio": velocidad_promedio_grupo,
            "Corridas": corridas_grupo
        }

    # Botón de Descarga actualizado en la barra lateral
    st.sidebar.markdown("---")
    st.sidebar.subheader("📄 Descarga de Informe")
    try:
        efecto_agitacion_datos_pdf = []
        for fruta in frutas_base:
            cond_con = f"{fruta} - Con Agitación"
            cond_sin = f"{fruta} - Sin Agitación"
            if cond_con in datos_agrupados and cond_sin in datos_agrupados:
                c_con_final = datos_agrupados[cond_con]["ConcProm"][-1]
                c_sin_final = datos_agrupados[cond_sin]["ConcProm"][-1]
                dif_abs = c_con_final - c_sin_final
                dif_porc = (dif_abs / c_sin_final) * 100 if c_sin_final > 0 else 0.0
                efecto_agitacion_datos_pdf.append({
                    "Matriz / Fruta": fruta,
                    "Conc. Final Con Agit. (g/L)": f"{c_con_final:.2f}",
                    "Conc. Final Sin Agit. (g/L)": f"{c_sin_final:.2f}",
                    "Diferencia Absoluta (g/L)": f"{dif_abs:.2f}",
                    "Efecto Porcentual Agitación (%)": f"{dif_porc:.2f}%"
                })

        ruta_pdf = generar_pdf_informe(
            datos_agrupados, m, b, r2, volumen_agua, masa_fruta, efecto_agitacion_datos_pdf, tiempo_muestreo, frutas_base
        )
        with open(ruta_pdf, "rb") as archivo_pdf:
            st.sidebar.download_button(
                label="📥 Descargar Informe PDF Completo",
                data=archivo_pdf,
                file_name="informe_cinetica_completo.pdf",
                mime="application/pdf",
                use_container_width=True
            )
    except Exception as e:
        st.sidebar.error(f"Error generando PDF: {e}")

    tabs = st.tabs([f"🧪 {g}" for g in grupos_unicos] + ["📊 Tabla Global y Gráficos", "⚡ Velocidades & Efecto Agitación", "📈 Extracción Relativa (Erel)"])

    for idx, grupo in enumerate(grupos_unicos):
        d = datos_agrupados[grupo]
        with tabs[idx]:
            st.write(f"### Condición: **{grupo}** ({len(d['Corridas'])} réplica(s) agrupadas)")

            st.write("#### Resumen Estadístico Completo (Promedio ± SD, CV, Masa, Extracción y Rendimiento)")
            tabla_resumen = {
                "Tiempo (min)": tiempo_muestreo,
                "Conc. Promedio (g/L)": [f"{v:.2f}" for v in d["ConcProm"]],
                "Desv. Estándar (± SD)": [f"{v:.2f}" for v in d["ConcStd"]],
                "Coef. de Variación (CV %)": [f"{v:.2f}%" for v in d["CV"]],
                "Masa Soluto Extractor (g)": [f"{v:.2f}" for v in d["MasaProm"]],
                "Extracción Relativa Corr. (%)": [f"{v:.2f}%" for v in d["ExtProm"]],
                "Rendimiento Aparente (%)": [f"{v:.2f}%" for v in d["RendProm"]],
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
            
            ax_g.errorbar(tiempo_muestreo, d["ConcProm"], yerr=d["ConcStd"], fmt="o-", color="black", linewidth=2, capsize=4, label="Promedio ± SD")
            ax_g.set_xlabel("Tiempo (min)")
            ax_g.set_ylabel("Concentración (g/L)")
            ax_g.set_title(f"Cinética con Réplicas: {grupo}")
            ax_g.grid(True)
            ax_g.legend()
            st.pyplot(fig_g)

    # --- PANEL DE SELECCIÓN CON CHECKBOXES ---
    st.markdown("---")
    st.subheader("🎛️ Panel de Control de Visualización")
    col_chk1, col_chk2 = st.columns(2)

    with col_chk1:
        st.markdown("##### 🔍 Réplicas Individuales")
        corridas_seleccionadas = []
        for item in historial:
            if st.checkbox(item["EtiquetaCompleta"], value=False, key=f"chk_corrida_{item['EtiquetaCompleta']}"):
                corridas_seleccionadas.append(item)

    with col_chk2:
        st.markdown("##### 📊 Promedios de Grupos")
        grupos_seleccionados = []
        for grupo in grupos_unicos:
            if st.checkbox(f"Promedio: {grupo}", value=True, key=f"chk_grupo_{grupo}"):
                grupos_seleccionados.append(grupo)

    # Pestaña de Tabla Global y Gráfica Global
    with tabs[len(grupos_unicos)]:
        st.subheader("📋 Tabla Consolidada de Todos los Grupos")
        tabla_global = {"Tiempo (min)": tiempo_muestreo}
        for grupo in grupos_unicos:
            tabla_global[f"{grupo} (g/L)"] = [f"{v:.2f}" for v in datos_agrupados[grupo]["ConcProm"]]
            tabla_global[f"{grupo} (CV %)"] = [f"{v:.2f}%" for v in datos_agrupados[grupo]["CV"]]
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
            st.warning("⚠️ Selecciona al menos un grupo o réplica en el panel superior.")

    # Pestaña de Velocidades y Efecto de Agitación (Incluye Gráfico de Efecto % vs Tiempo)
    with tabs[len(grupos_unicos) + 1]:
        st.subheader("⚡ Análisis de Efecto de Agitación")
        
        efecto_agitacion_datos = []
        for fruta in frutas_base:
            cond_con = f"{fruta} - Con Agitación"
            cond_sin = f"{fruta} - Sin Agitación"
            
            if cond_con in datos_agrupados and cond_sin in datos_agrupados:
                c_con_final = datos_agrupados[cond_con]["ConcProm"][-1]
                c_sin_final = datos_agrupados[cond_sin]["ConcProm"][-1]
                
                dif_abs = c_con_final - c_sin_final
                dif_porc = (dif_abs / c_sin_final) * 100 if c_sin_final > 0 else 0.0
                
                efecto_agitacion_datos.append({
                    "Matriz / Fruta": fruta,
                    "Conc. Final Con Agit. (g/L)": f"{c_con_final:.2f}",
                    "Conc. Final Sin Agit. (g/L)": f"{c_sin_final:.2f}",
                    "Diferencia Absoluta (g/L)": f"{dif_abs:.2f}",
                    "Efecto Porcentual Agitación (%)": f"{dif_porc:.2f}%"
                })
        
        if len(efecto_agitacion_datos) > 0:
            st.dataframe(efecto_agitacion_datos, use_container_width=True)
        else:
            st.info("💡 Para calcular automáticamente el efecto de la agitación, registra al menos una fruta con ambas condiciones.")

        st.markdown("---")
        st.subheader("📈 Evolución Temporal del Efecto Porcentual de Agitación (%) vs Tiempo")
        if len(frutas_base) > 0:
            fig_ef, ax_ef = plt.subplots(figsize=(9, 4.5))
            hay_curvas_ef = False
            for fruta in frutas_base:
                cond_con = f"{fruta} - Con Agitación"
                cond_sin = f"{fruta} - Sin Agitación"
                if cond_con in datos_agrupados and cond_sin in datos_agrupados:
                    c_con = datos_agrupados[cond_con]["ConcProm"]
                    c_sin = datos_agrupados[cond_sin]["ConcProm"]
                    efecto_t = np.where(c_sin > 0, ((c_con - c_sin) / c_sin) * 100, 0.0)
                    ax_ef.plot(tiempo_muestreo, efecto_t, marker="o", linewidth=2, label=fruta)
                    hay_curvas_ef = True

            if hay_curvas_ef:
                ax_ef.set_xlabel("Tiempo (min)")
                ax_ef.set_ylabel("Efecto de Agitación (%)")
                ax_ef.set_title("Efecto Porcentual de Agitación a lo largo del Tiempo")
                ax_ef.grid(True)
                ax_ef.legend()
                st.pyplot(fig_ef)
            else:
                st.info("💡 Registra parejas completas (Con y Sin agitación para una misma fruta) para trazar esta gráfica.")

        st.markdown("---")
        st.subheader("📊 Comparación Gráfica de Velocidades Promedio")
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

    # Pestaña de Extracción Relativa Corregida (Erel %) vs Tiempo
    with tabs[len(grupos_unicos) + 2]:
        st.subheader("📈 Extracción Relativa Corregida Erel (%) vs Tiempo")
        st.markdown("Esta gráfica muestra la fracción normalizada de soluto extraído respecto al valor final para cada condición experimental.")
        
        if len(grupos_seleccionados) > 0:
            fig_er, ax_er = plt.subplots(figsize=(9, 5))
            for grupo in grupos_seleccionados:
                d = datos_agrupados[grupo]
                ax_er.plot(tiempo_muestreo, d["ExtProm"], marker="o", linewidth=2, label=grupo)
            
            ax_er.set_xlabel("Tiempo (min)")
            ax_er.set_ylabel("Extracción Relativa Corregida Erel (%)")
            ax_er.set_title("Cinética de Extracción Relativa Normalizada")
            ax_er.grid(True)
            ax_er.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
            plt.tight_layout()
            st.pyplot(fig_er)
        else:
            st.warning("⚠️ Selecciona al menos un grupo en el panel superior para visualizar su extracción relativa.")
else:
    st.info("👈 Ingresa los datos de calibración y registra tus réplicas en la barra lateral para generar el informe PDF.")
