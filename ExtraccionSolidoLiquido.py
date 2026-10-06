import tempfile
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import linregress
from fpdf import FPDF
import streamlit as st
import pandas as pd

# Configuración inicial de la página de Streamlit
st.set_page_config(
    page_title="Cinética de Extracción Sólido-Líquido",
    page_icon="🍇",
    layout="wide"
)

# ==========================================
# --- FUNCIÓN PARA GENERAR EL PDF COMPLETO ---
# ==========================================
def generar_pdf_informe(datos_agrupados, m, b, r2, volumen_agua, masa_fruta, efecto_agitacion_datos, efecto_agitacion_temporal, tiempo_muestreo, frutas_base):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "Informe Completo - Cinetica de Extraccion Solido-Liquido", ln=True, align="C")
    pdf.ln(2)
    
    # 1. Parámetros Generales y Calibración
    pdf.set_font("Arial", "B", 10)
    pdf.cell(0, 6, "1. Parametros Generales y Calibracion:", ln=True)
    pdf.set_font("Arial", "", 9)
    pdf.cell(0, 5, f"- Volumen de agua: {volumen_agua:.3f} L | Masa de fruta: {masa_fruta:.2f} g", ln=True)
    pdf.cell(0, 5, f"- Curva de Calibrado: y = {m:.4f}x + {b:.4f}  (R2 = {r2:.4f})", ln=True)
    pdf.ln(4)
    
    # 2. Resultados Estadísticos por Condición
    pdf.set_font("Arial", "B", 10)
    pdf.cell(0, 6, "2. Resultados Estadisticos por Condicion (Absorbancia y Concentracion):", ln=True)
    pdf.ln(2)
    
    for grupo, d in datos_agrupados.items():
        if pdf.get_y() > 220:
            pdf.add_page()
            
        pdf.set_font("Arial", "B", 9)
        pdf.cell(0, 6, f" Condicion: {grupo} ({len(d['Corridas'])} replicas)", ln=True)
        
        pdf.set_font("Arial", "B", 7)
        pdf.cell(12, 5, "T(min)", 1, 0, "C")
        pdf.cell(32, 5, "ABS Prom ± SD", 1, 0, "C")
        pdf.cell(24, 5, "Conc.(g/L)", 1, 0, "C")
        pdf.cell(18, 5, "SD (±)", 1, 0, "C")
        pdf.cell(18, 5, "CV (%)", 1, 0, "C")
        pdf.cell(24, 5, "Masa Ext.(g)", 1, 0, "C")
        pdf.cell(25, 5, "Ext.Corr(%)", 1, 0, "C")
        pdf.cell(24, 5, "Rend.(%)", 1, 1, "C")
        
        pdf.set_font("Arial", "", 7)
        for i, t in enumerate(d["Tiempos"]):
            if pdf.get_y() > 275:
                pdf.add_page()
                pdf.set_font("Arial", "B", 7)
                pdf.cell(12, 5, "T(min)", 1, 0, "C")
                pdf.cell(32, 5, "ABS Prom ± SD", 1, 0, "C")
                pdf.cell(24, 5, "Conc.(g/L)", 1, 0, "C")
                pdf.cell(18, 5, "SD (±)", 1, 0, "C")
                pdf.cell(18, 5, "CV (%)", 1, 0, "C")
                pdf.cell(24, 5, "Masa Ext.(g)", 1, 0, "C")
                pdf.cell(25, 5, "Ext.Corr(%)", 1, 0, "C")
                pdf.cell(24, 5, "Rend.(%)", 1, 1, "C")
                pdf.set_font("Arial", "", 7)

            abs_str = f"{d['AbsProm'][i]:.3f} ± {d['AbsStd'][i]:.3f}"
            pdf.cell(12, 5, f"{t}", 1, 0, "C")
            pdf.cell(32, 5, abs_str, 1, 0, "C")
            pdf.cell(24, 5, f"{d['ConcProm'][i]:.2f}", 1, 0, "C")
            pdf.cell(18, 5, f"{d['ConcStd'][i]:.2f}", 1, 0, "C")
            pdf.cell(18, 5, f"{d['CV'][i]:.1f}%", 1, 0, "C")
            pdf.cell(24, 5, f"{d['MasaProm'][i]:.2f}", 1, 0, "C")
            pdf.cell(25, 5, f"{d['ExtProm'][i]:.1f}%", 1, 0, "C")
            pdf.cell(24, 5, f"{d['RendProm'][i]:.2f}%", 1, 1, "C")
        pdf.ln(5)

    # 3. Velocidades Promedio por Intervalos (con Gráfico de Barras en página exclusiva)
    if len(tiempo_muestreo) > 1:
        pdf.add_page()
        pdf.set_font("Arial", "B", 11)
        pdf.cell(0, 8, "3. Velocidades Promedio de Extraccion por Intervalos", ln=True)
        pdf.ln(2)
        
        for grupo, d in datos_agrupados.items():
            if pdf.get_y() > 230:
                pdf.add_page()
            pdf.set_font("Arial", "B", 9)
            pdf.cell(0, 5, f" Condicion: {grupo}", ln=True)
            
            pdf.set_font("Arial", "B", 8)
            pdf.cell(50, 5, "Intervalo de tiempo (min)", 1, 0, "C")
            pdf.cell(70, 5, "Velocidad promedio ((g/L)/min)", 1, 1, "C")
            
            pdf.set_font("Arial", "", 8)
            for ti, tf, vm in zip(tiempo_muestreo[:-1], tiempo_muestreo[1:], d["VelocidadPromedio"]):
                if pdf.get_y() > 275:
                    pdf.add_page()
                pdf.cell(50, 5, f"{int(ti)} a {int(tf)}", 1, 0, "C")
                pdf.cell(70, 5, f"{vm:.4f}", 1, 1, "C")
            pdf.ln(3)

        # Gráfico de Barras de Velocidades Promedio (Página única y exclusiva)
        pdf.add_page()
        pdf.set_font("Arial", "B", 11)
        pdf.cell(0, 8, "Grafico de Velocidades Promedio por Intervalos", ln=True)
        pdf.ln(3)

        fig_vel, ax_vel = plt.subplots(figsize=(8, 4.5))
        intervalos_str = [f"{int(tiempo_muestreo[i])}-{int(tiempo_muestreo[i+1])}" for i in range(len(tiempo_muestreo)-1)]
        x_indices = np.arange(len(intervalos_str))
        ancho_barra = 0.8 / max(1, len(datos_agrupados))

        for idx, (grupo, d) in enumerate(datos_agrupados.items()):
            offset = (idx - len(datos_agrupados)/2) * ancho_barra + ancho_barra/2
            ax_vel.bar(x_indices + offset, d["VelocidadPromedio"], width=ancho_barra, label=grupo)

        ax_vel.set_xlabel("Intervalos de Tiempo (min)")
        ax_vel.set_ylabel("Velocidad Promedio ((g/L)/min)")
        ax_vel.set_title("Comparativa de Velocidades de Extracción por Intervalos")
        ax_vel.set_xticks(x_indices)
        ax_vel.set_xticklabels(intervalos_str)
        ax_vel.grid(True, axis="y")
        ax_vel.legend(fontsize=6, bbox_to_anchor=(1.05, 1), loc='upper left')

        img_vel_tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
        plt.savefig(img_vel_tmp.name, bbox_inches="tight", dpi=150)
        plt.close(fig_vel)

        pdf.image(img_vel_tmp.name, x=15, y=pdf.get_y() + 2, w=170)
        pdf.ln(5)

    # 4. Análisis del Efecto de la Agitación (Temporal y Final)
    if len(efecto_agitacion_temporal) > 0 or len(efecto_agitacion_datos) > 0:
        pdf.add_page()
        pdf.set_font("Arial", "B", 11)
        pdf.cell(0, 8, "4. Analisis del Efecto de la Agitacion (Temporal y Final)", ln=True)
        pdf.ln(2)
        
        if len(efecto_agitacion_temporal) > 0:
            pdf.set_font("Arial", "B", 9)
            pdf.cell(0, 6, "Diferencias de ABS y Efecto de Agitacion por Tiempo:", ln=True)
            pdf.set_font("Arial", "B", 7)
            pdf.cell(35, 5, "Fruta / Matriz", 1, 0, "C")
            pdf.cell(20, 5, "Tiempo (m)", 1, 0, "C")
            pdf.cell(30, 5, "ABS Con Agit.", 1, 0, "C")
            pdf.cell(30, 5, "ABS Sin Agit.", 1, 0, "C")
            pdf.cell(30, 5, "Dif. Delta ABS", 1, 0, "C")
            pdf.cell(30, 5, "Efecto Agit.(%)", 1, 1, "C")
            
            pdf.set_font("Arial", "", 7)
            for et in efecto_agitacion_temporal:
                if pdf.get_y() > 275:
                    pdf.add_page()
                pdf.cell(35, 5, f"{et['Fruta']}", 1, 0, "L")
                pdf.cell(20, 5, f"{et['Tiempo']}", 1, 0, "C")
                pdf.cell(30, 5, f"{et['ABS Con']:.3f}", 1, 0, "C")
                pdf.cell(30, 5, f"{et['ABS Sin']:.3f}", 1, 0, "C")
                pdf.cell(30, 5, f"{et['Delta ABS']:.3f}", 1, 0, "C")
                pdf.cell(30, 5, f"{et['Efecto (%)']:.1f}%", 1, 1, "C")
            pdf.ln(4)

        if len(efecto_agitacion_datos) > 0:
            pdf.set_font("Arial", "B", 9)
            pdf.cell(0, 6, "Resumen Punto Final:", ln=True)
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
            pdf.ln(5)

        # Gráfico de Absorbancia vs Tiempo (Con vs Sin Agitación) en PDF
        pdf.add_page()
        pdf.set_font("Arial", "B", 11)
        pdf.cell(0, 8, "Grafico de Absorbancia vs Tiempo (Con vs. Sin Agitacion)", ln=True)
        pdf.ln(3)

        fig_abs_temp, ax_abs_temp = plt.subplots(figsize=(8, 4))
        for fruta in frutas_base:
            cond_con = f"{fruta} - Con Agitación"
            cond_sin = f"{fruta} - Sin Agitación"
            if cond_con in datos_agrupados and cond_sin in datos_agrupados:
                ax_abs_temp.plot(tiempo_muestreo, datos_agrupados[cond_con]["AbsProm"], marker="o", label=f"{fruta} - Con Agit.")
                ax_abs_temp.plot(tiempo_muestreo, datos_agrupados[cond_sin]["AbsProm"], marker="s", linestyle="--", label=f"{fruta} - Sin Agit.")

        ax_abs_temp.set_xlabel("Tiempo (min)")
        ax_abs_temp.set_ylabel("Absorbancia (600 nm)")
        ax_abs_temp.set_title("Evolución Temporal de la Absorbancia (Con vs. Sin Agitación)")
        ax_abs_temp.grid(True)
        ax_abs_temp.legend(fontsize=6, bbox_to_anchor=(1.05, 1), loc='upper left')

        img_abs_tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
        plt.savefig(img_abs_tmp.name, bbox_inches="tight", dpi=150)
        plt.close(fig_abs_temp)

        pdf.image(img_abs_tmp.name, x=15, y=pdf.get_y() + 2, w=170)
        pdf.ln(5)

        # Gráfico de Diferencia de Absorbancia (Delta ABS) vs Tiempo en PDF
        pdf.add_page()
        pdf.set_font("Arial", "B", 11)
        pdf.cell(0, 8, "Grafico de Diferencia de Absorbancia (Delta ABS) vs Tiempo", ln=True)
        pdf.ln(3)

        fig_dif_temp, ax_dif_temp = plt.subplots(figsize=(8, 4))
        for fruta in frutas_base:
            cond_con = f"{fruta} - Con Agitación"
            cond_sin = f"{fruta} - Sin Agitación"
            if cond_con in datos_agrupados and cond_sin in datos_agrupados:
                abs_con = datos_agrupados[cond_con]["AbsProm"]
                abs_sin = datos_agrupados[cond_sin]["AbsProm"]
                delta_abs = abs_con - abs_sin
                ax_dif_temp.plot(tiempo_muestreo, delta_abs, marker="o", label=f"Delta ABS {fruta}")

        ax_dif_temp.set_xlabel("Tiempo (min)")
        ax_dif_temp.set_ylabel("Diferencia de Absorbancia ($\\Delta$ABS)")
        ax_dif_temp.set_title("Evolución Temporal de la Diferencia de Absorbancia (Con - Sin)")
        ax_dif_temp.grid(True)
        ax_dif_temp.legend(fontsize=7)

        img_dif_tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
        plt.savefig(img_dif_tmp.name, bbox_inches="tight", dpi=150)
        plt.close(fig_dif_temp)

        pdf.image(img_dif_tmp.name, x=15, y=pdf.get_y() + 2, w=180)
        pdf.ln(5)

        # Gráfico de Porcentaje de Efecto de Agitación vs Tiempo en PDF
        pdf.add_page()
        pdf.set_font("Arial", "B", 11)
        pdf.cell(0, 8, "Grafico de Porcentaje de Efecto de Agitacion (%) vs Tiempo", ln=True)
        pdf.ln(3)

        fig_ef_temp, ax_ef_temp = plt.subplots(figsize=(8, 4))
        for fruta in frutas_base:
            cond_con = f"{fruta} - Con Agitación"
            cond_sin = f"{fruta} - Sin Agitación"
            if cond_con in datos_agrupados and cond_sin in datos_agrupados:
                abs_con = datos_agrupados[cond_con]["AbsProm"]
                abs_sin = datos_agrupados[cond_sin]["AbsProm"]
                efecto_porc_t = np.where(abs_sin > 0, ((abs_con - abs_sin) / abs_sin) * 100, 0.0)
                ax_ef_temp.plot(tiempo_muestreo, efecto_porc_t, marker="o", label=fruta)

        ax_ef_temp.set_xlabel("Tiempo (min)")
        ax_ef_temp.set_ylabel("Efecto de Agitación (%)")
        ax_ef_temp.set_title("Evolución Temporal del Porcentaje de Efecto de Agitación")
        ax_ef_temp.grid(True)
        ax_ef_temp.legend(fontsize=7)

        img_ef_tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
        plt.savefig(img_ef_tmp.name, bbox_inches="tight", dpi=150)
        plt.close(fig_ef_temp)

        pdf.image(img_ef_tmp.name, x=15, y=pdf.get_y() + 2, w=180)
        pdf.ln(5)

    # 5. Gráfica Global Comparativa en página única y exclusiva
    pdf.add_page()
    pdf.set_font("Arial", "B", 11)
    pdf.cell(0, 8, "5. Grafica Comparativa Global", ln=True)
    pdf.ln(3)
    
    fig_temp2, ax_temp2 = plt.subplots(figsize=(8, 4.5))
    for grupo, d in datos_agrupados.items():
        ax_temp2.errorbar(d["Tiempos"], d["ConcProm"], yerr=d["ConcStd"], marker="o", capsize=3, label=grupo)
    ax_temp2.set_xlabel("Tiempo (min)")
    ax_temp2.set_ylabel("Concentracion (g/L)")
    ax_temp2.set_title("Cinetica de Extraccion Global")
    ax_temp2.grid(True)
    ax_temp2.legend(fontsize=7, bbox_to_anchor=(1.05, 1), loc='upper left')
    
    img_tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
    plt.savefig(img_tmp_file.name, bbox_inches="tight", dpi=150)
    plt.close(fig_temp2)
    
    pdf.image(img_tmp_file.name, x=15, y=pdf.get_y() + 2, w=170)
    
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    pdf.output(tmp.name)
    return tmp.name


# ==========================================
# --- APLICACIÓN PRINCIPAL STREAMLIT ---
# ==========================================

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

# --- PARÁMETROS GENERALES Y CALIBRACIÓN (BARRA LATERAL) ---
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

# Procesamiento de la Curva de Calibración
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

# --- INGRESO DE DATOS EXPERIMENTALES (BARRA LATERAL) ---
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
            st.sidebar.error("⚠ La cantidad de valores de ABS experimental debe coincidir con los Tiempos de muestreo.")
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

# ==========================================
# --- GESTIÓN Y ELIMINACIÓN DE RÉPLICAS ---
# ==========================================
if len(st.session_state.HistorialExtraccion) > 0:
    with st.sidebar.expander("🛠 Administrar / Borrar Réplicas"):
        for i, item in enumerate(st.session_state.HistorialExtraccion):
            cols_adm = st.columns([3, 1])
            cols_adm[0].write(item["EtiquetaCompleta"])
            if cols_adm[1].button("❌", key=f"del_rep_{i}"):
                st.session_state.HistorialExtraccion.pop(i)
                st.rerun()

# ==========================================
# --- AGRUPAR Y PROCESAR ESTADÍSTICAS ---
# ==========================================
historial = st.session_state.HistorialExtraccion

if len(historial) > 0:
    st.markdown("---")
    st.subheader(f"📋 Panel de Resultados y Control ({len(historial)} registros totales)")

    grupos_unicos = sorted(list(set(item["Grupo"] for item in historial)))
    frutas_base = sorted(list(set([g.split(" - ")[0] for g in grupos_unicos if " - " in g])))
    
    datos_agrupados = {}
    for grupo in grupos_unicos:
        corridas_grupo = [item for item in historial if item["Grupo"] == grupo]
        matriz_abs = np.array([c["ABSExperimental"] for c in corridas_grupo])
        matriz_conc = np.array([c["Concentracion"] for c in corridas_grupo])
        matriz_masa = np.array([c["MasaAparente"] for c in corridas_grupo])
        matriz_ext = np.array([c["ExtraccionRelativa"] for c in corridas_grupo])
        matriz_rend = np.array([c["RendimientoAparente"] for c in corridas_grupo])

        abs_prom = np.mean(matriz_abs, axis=0)
        abs_std = np.std(matriz_abs, axis=0, ddof=1) if len(corridas_grupo) > 1 else np.zeros_like(abs_prom)

        conc_prom = np.mean(matriz_conc, axis=0)
        conc_std = np.std(matriz_conc, axis=0, ddof=1) if len(corridas_grupo) > 1 else np.zeros_like(conc_std)
        cv_opcional = np.where(conc_prom > 0, (conc_std / conc_prom) * 100, 0.0)

        masa_prom = np.mean(matriz_masa, axis=0)
        ext_prom = np.mean(matriz_ext, axis=0)
        rend_prom = np.mean(matriz_rend, axis=0)

        tm = np.diff(tiempo_muestreo)
        c_diff = np.diff(conc_prom)
        velocidad_promedio_grupo = c_diff / tm if np.all(tm > 0) else np.zeros_like(c_diff)

        datos_agrupados[grupo] = {
            "Tiempos": tiempo_muestreo,
            "AbsProm": abs_prom,
            "AbsStd": abs_std,
            "ConcProm": conc_prom,
            "ConcStd": conc_std,
            "CV": cv_opcional,
            "MasaProm": masa_prom,
            "ExtProm": ext_prom,
            "RendProm": rend_prom,
            "VelocidadPromedio": velocidad_promedio_grupo,
            "Corridas": corridas_grupo
        }

    # Preparar datos de agitación temporal para la barra lateral y PDF
    efecto_agitacion_temporal_pdf = []
    for fruta in frutas_base:
        cond_con = f"{fruta} - Con Agitación"
        cond_sin = f"{fruta} - Sin Agitación"
        if cond_con in datos_agrupados and cond_sin in datos_agrupados:
            abs_con_arr = datos_agrupados[cond_con]["AbsProm"]
            abs_sin_arr = datos_agrupados[cond_sin]["AbsProm"]
            for idx_t, t_val in enumerate(tiempo_muestreo):
                ac = abs_con_arr[idx_t]
                as_ = abs_sin_arr[idx_t]
                delta = ac - as_
                efecto_porc = (delta / as_) * 100 if as_ > 0 else 0.0
                efecto_agitacion_temporal_pdf.append({
                    "Fruta": fruta,
                    "Tiempo": int(t_val),
                    "ABS Con": ac,
                    "ABS Sin": as_,
                    "Delta ABS": delta,
                    "Efecto (%)": efecto_porc
                })

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

    # Botón de Descarga en Barra Lateral
    st.sidebar.markdown("---")
    st.sidebar.subheader("📄 Descarga de Informe")
    try:
        ruta_pdf = generar_pdf_informe(
            datos_agrupados, m, b, r2, volumen_agua, masa_fruta, efecto_agitacion_datos_pdf, efecto_agitacion_temporal_pdf, tiempo_muestreo, frutas_base
        )
        with open(ruta_pdf, "rb") as archivo_pdf:
            st.sidebar.download_button(
                label="📥 Descargar Informe PDF Completo",
                data=archivo_pdf,
                file_name="informe_cinetica_completo.pdf",
                mime="application/pdf"
            )
    except Exception as e:
        st.sidebar.error(f"Error generando PDF: {e}")

    # Creación de Pestañas Principales
    tabs = st.tabs([f"🧪 {g}" for g in grupos_unicos] + ["📊 Tabla Global y Gráficos", "⚡ Velocidades & Efecto Agitación", "📈 Extracción Relativa (Erel)"])

    for idx, grupo in enumerate(grupos_unicos):
        d = datos_agrupados[grupo]
        with tabs[idx]:
            st.write(f"### Condición: **{grupo}** ({len(d['Corridas'])} réplica(s) agrupadas)")

            st.write("#### Resumen Estadístico Completo (Absorbancia Prom ± SD, Concentración, CV, Masa, Extracción y Rendimiento)")
            tabla_resumen = {
                "Tiempo (min)": [int(t) for t in tiempo_muestreo],
                "ABS Prom ± SD": [f"{d['AbsProm'][i]:.3f} ± {d['AbsStd'][i]:.3f}" for i in range(len(tiempo_muestreo))],
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
                tabla_2_datos = {
                    "Intervalo de tiempo (min)": [f"{int(ti)} a {int(tf)}" for ti, tf in zip(tiempo_muestreo[:-1], tiempo_muestreo[1:])],
                    "Velocidad promedio ((g/L)/min)": [f"{vm:.4f}" for vm in d["VelocidadPromedio"]]
                }
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

    # Pestaña: Tabla Global y Gráfica Global
    with tabs[len(grupos_unicos)]:
        st.subheader("📋 Tabla Consolidada de Todos los Grupos")
        tabla_global = {"Tiempo (min)": [int(t) for t in tiempo_muestreo]}
        for grupo in grupos_unicos:
            tabla_global[f"{grupo} (ABS Prom ± SD)"] = [f"{datos_agrupados[grupo]['AbsProm'][i]:.3f} ± {datos_agrupados[grupo]['AbsStd'][i]:.3f}" for i in range(len(tiempo_muestreo))]
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

    # Pestaña: Velocidades y Efecto de Agitación
    with tabs[len(grupos_unicos) + 1]:
        st.subheader("⚡ Análisis de Velocidades Promedio por Intervalos")
        if len(tiempo_muestreo) > 1:
            fig_vel_web, ax_vel_web = plt.subplots(figsize=(8, 4))
            intervalos_str = [f"{int(tiempo_muestreo[i])} a {int(tiempo_muestreo[i+1])}" for i in range(len(tiempo_muestreo)-1)]
            x_indices = np.arange(len(intervalos_str))
            ancho_barra = 0.8 / max(1, len(datos_agrupados))

            for idx, (grupo, d) in enumerate(datos_agrupados.items()):
                offset = (idx - len(datos_agrupados)/2) * ancho_barra + ancho_barra/2
                ax_vel_web.bar(x_indices + offset, d["VelocidadPromedio"], width=ancho_barra, label=grupo)

            ax_vel_web.set_xlabel("Intervalos de Tiempo (min)")
            ax_vel_web.set_ylabel("Velocidad Promedio ((g/L)/min)")
            ax_vel_web.set_title("Gráfico de Barras: Velocidad Promedio de Extracción")
            ax_vel_web.set_xticks(x_indices)
            ax_vel_web.set_xticklabels(intervalos_str)
            ax_vel_web.grid(True, axis="y")
            ax_vel_web.legend(fontsize=7, bbox_to_anchor=(1.05, 1), loc='upper left')
            plt.tight_layout()
            st.pyplot(fig_vel_web)

        st.markdown("---")
        st.subheader("⚡ Análisis de Efecto de Agitación (Temporal y Final)")
        
        if len(efecto_agitacion_temporal_pdf) > 0:
            st.markdown("##### 🕒 Diferencia de Absorbancia ($\\Delta$ABS) y Efecto Porcentual para Cada Tiempo")
            df_agit_temp = pd.DataFrame(efecto_agitacion_temporal_pdf)
            df_agit_temp["ABS Con"] = df_agit_temp["ABS Con"].map(lambda x: f"{x:.3f}")
            df_agit_temp["ABS Sin"] = df_agit_temp["ABS Sin"].map(lambda x: f"{x:.3f}")
            df_agit_temp["Delta ABS"] = df_agit_temp["Delta ABS"].map(lambda x: f"{x:.3f}")
            df_agit_temp["Efecto (%)"] = df_agit_temp["Efecto (%)"].map(lambda x: f"{x:.1f}%")
            st.dataframe(df_agit_temp, use_container_width=True)
        else:
            st.info("💡 Para mostrar la tabla temporal de agitación, registra al menos una fruta con ambas condiciones ('Con Agitación' y 'Sin Agitación').")

        st.markdown("---")
        st.markdown("##### 📌 Resumen Punto Final")
        if len(efecto_agitacion_datos_pdf) > 0:
            st.dataframe(efecto_agitacion_datos_pdf, use_container_width=True)
        else:
            st.info("💡 Registra pares de condiciones para ver el resumen de punto final.")

        st.markdown("---")
        st.subheader("📈 Gráfica de Evolución Temporal de la Absorbancia (Con vs. Sin Agitación)")
        fig_abs_web, ax_abs_web = plt.subplots(figsize=(8, 4))
        hay_datos_abs = False
        for fruta in frutas_base:
            cond_con = f"{fruta} - Con Agitación"
            cond_sin = f"{fruta} - Sin Agitación"
            if cond_con in datos_agrupados and cond_sin in datos_agrupados:
                ax_abs_web.plot(tiempo_muestreo, datos_agrupados[cond_con]["AbsProm"], marker="o", label=f"{fruta} - Con Agit.")
                ax_abs_web.plot(tiempo_muestreo, datos_agrupados[cond_sin]["AbsProm"], marker="s", linestyle="--", label=f"{fruta} - Sin Agit.")
                hay_datos_abs = True
        
        if hay_datos_abs:
            ax_abs_web.set_xlabel("Tiempo (min)")
            ax_abs_web.set_ylabel("Absorbancia (600 nm)")
            ax_abs_web.set_title("Comparativa de Absorbancia: Con vs. Sin Agitación")
            ax_abs_web.grid(True)
            ax_abs_web.legend(fontsize=6, bbox_to_anchor=(1.05, 1), loc='upper left')
            plt.tight_layout()
            st.pyplot(fig_abs_web)
        else:
            st.info("💡 Se necesitan pares de condiciones para graficar la comparativa de absorbancias.")

        st.markdown("---")
        st.subheader("📈 Gráfica de Diferencia de Absorbancia ($\\Delta$ABS) vs Tiempo")
        fig_dif_web, ax_dif_web = plt.subplots(figsize=(8, 4))
        hay_datos_dif = False
        for fruta in frutas_base:
            cond_con = f"{fruta} - Con Agitación"
            cond_sin = f"{fruta} - Sin Agitación"
            if cond_con in datos_agrupados and cond_sin in datos_agrupados:
                abs_con = datos_agrupados[cond_con]["AbsProm"]
                abs_sin = datos_agrupados[cond_sin]["AbsProm"]
                delta_abs = abs_con - abs_sin
                ax_dif_web.plot(tiempo_muestreo, delta_abs, marker="o", label=f"Delta ABS {fruta}")
                hay_datos_dif = True
        
        if hay_datos_dif:
            ax_dif_web.set_xlabel("Tiempo (min)")
            ax_dif_web.set_ylabel("Diferencia de Absorbancia ($\\Delta$ABS)")
            ax_dif_web.set_title("Evolución Temporal de la Diferencia de Absorbancia (Con - Sin)")
            ax_dif_web.grid(True)
            ax_dif_web.legend(fontsize=7)
            st.pyplot(fig_dif_web)
        else:
            st.info("💡 Se necesitan pares de condiciones para graficar la diferencia de absorbancias.")

        st.markdown("---")
        st.subheader("📈 Gráfica de Porcentaje de Efecto de Agitación vs Tiempo")
        fig_ef, ax_ef = plt.subplots(figsize=(8, 4))
        hay_datos_ef = False
        for fruta in frutas_base:
            cond_con = f"{fruta} - Con Agitación"
            cond_sin = f"{fruta} - Sin Agitación"
            if cond_con in datos_agrupados and cond_sin in datos_agrupados:
                abs_con = datos_agrupados[cond_con]["AbsProm"]
                abs_sin = datos_agrupados[cond_sin]["AbsProm"]
                efecto_porc_t = np.where(abs_sin > 0, ((abs_con - abs_sin) / abs_sin) * 100, 0.0)
                ax_ef.plot(tiempo_muestreo, efecto_porc_t, marker="o", label=f"Efecto % {fruta}")
                hay_datos_ef = True
        
        if hay_datos_ef:
            ax_ef.set_xlabel("Tiempo (min)")
            ax_ef.set_ylabel("Efecto de Agitación (%)")
            ax_ef.set_title("Evolución Temporal del Porcentaje de Efecto de Agitación")
            ax_ef.grid(True)
            ax_ef.legend(fontsize=7)
            st.pyplot(fig_ef)
        else:
            st.info("💡 Se necesitan pares de condiciones para graficar los porcentajes de efecto.")

    # Pestaña: Extracción Relativa (Erel %)
    with tabs[len(grupos_unicos) + 2]:
        st.subheader("📈 Extracción Relativa Corregida ($E_{rel}$ %) y Rendimiento")
        fig_er, ax_er = plt.subplots(figsize=(8, 4))
        for grupo in grupos_unicos:
            d = datos_agrupados[grupo]
            ax_er.plot(tiempo_muestreo, d["ExtProm"], marker="o", label=f"{grupo}")
        ax_er.set_xlabel("Tiempo (min)")
        ax_er.set_ylabel("Extracción Relativa Corregida ($E_{rel}$ %)")
        ax_er.set_title("Cinética de Extracción Relativa Normalizada")
        ax_er.grid(True)
        ax_er.legend(fontsize=7, bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.tight_layout()
        st.pyplot(fig_er)
