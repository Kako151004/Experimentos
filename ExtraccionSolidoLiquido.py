import tempfile
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import linregress
from fpdf import FPDF
import streamlit as st

st.set_page_config(
    page_title="Cinética de Extracción Sólido-Líquido", page_icon="🍇", layout="wide"
)

# --- FUNCIÓN PARA GENERAR EL PDF COMPLETO ---
def generar_pdf_informe(
    datos_agrupados,
    m,
    b,
    r2,
    volumen_agua,
    masa_fruta,
    efecto_agitacion_datos,
    efecto_por_tiempo_pdf,
    tiempo_muestreo,
    frutas_base,
):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 14)
    pdf.cell(
        0,
        10,
        "Informe Completo - Cinetica de Extraccion Solido-Liquido",
        ln=True,
        align="C",
    )
    pdf.ln(2)
    
    # 1. Parámetros Generales
    pdf.set_font("Arial", "B", 10)
    pdf.cell(0, 6, "1. Parametros Generales y Calibracion:", ln=True)
    pdf.set_font("Arial", "", 9)
    pdf.cell(
        0,
        5,
        f"- Volumen de agua: {volumen_agua:.3f} L | Masa de fruta: {masa_fruta:.2f} g",
        ln=True,
    )
    pdf.cell(
        0,
        5,
        f"- Curva de Calibrado: y = {m:.4f}x + {b:.4f}  (R2 = {r2:.4f})",
        ln=True,
    )
    pdf.ln(4)
    
    # 2. Resultados por Condición
    pdf.set_font("Arial", "B", 10)
    pdf.cell(
        0,
        6,
        "2. Resultados Estadisticos por Condicion (Absorbancia y Concentracion):",
        ln=True,
    )
    
    for grupo, d in datos_agrupados.items():
        pdf.set_font("Arial", "B", 9)
        pdf.cell(
            0, 5, f" Condicion: {grupo} ({len(d['Corridas'])} replicas)", ln=True
        )
        
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
            abs_str = f"{d['AbsProm'][i]:.3f} ± {d['AbsStd'][i]:.3f}"
            pdf.cell(12, 5, f"{t}", 1, 0, "C")
            pdf.cell(32, 5, abs_str, 1, 0, "C")
            pdf.cell(24, 5, f"{d['ConcProm'][i]:.2f}", 1, 0, "C")
            pdf.cell(18, 5, f"{d['ConcStd'][i]:.2f}", 1, 0, "C")
            pdf.cell(18, 5, f"{d['CV'][i]:.1f}%", 1, 0, "C")
            pdf.cell(24, 5, f"{d['MasaProm'][i]:.2f}", 1, 0, "C")
            pdf.cell(25, 5, f"{d['ExtProm'][i]:.1f}%", 1, 0, "C")
            pdf.cell(24, 5, f"{d['RendProm'][i]:.2f}%", 1, 1, "C")
        pdf.ln(3)

    # 3. Velocidades Promedio por Intervalos
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
            for ti, tf, vm in zip(
                tiempo_muestreo[:-1], tiempo_muestreo[1:], d["VelocidadPromedio"]
            ):
                pdf.cell(50, 5, f"{int(ti)} a {int(tf)}", 1, 0, "C")
                pdf.cell(70, 5, f"{vm:.4f}", 1, 1, "C")
            pdf.ln(2)

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
        
    # 4. Análisis de Efecto de Agitación (Punto Final y Desglose Temporal)
    if len(efecto_agitacion_datos) > 0:
        pdf.add_page()
        pdf.set_font("Arial", "B", 10)
        pdf.cell(
            0, 6, "4. Analisis del Efecto de la Agitacion (Punto Final):", ln=True
        )
        
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

        # Desglose Temporal en el PDF
        if len(efecto_por_tiempo_pdf) > 0:
            pdf.set_font("Arial", "B", 10)
            pdf.cell(
                0,
                6,
                "Desglose Detallado del Efecto de Agitacion por Cada Tiempo:",
                ln=True,
            )
            
            pdf.set_font("Arial", "B", 8)
            pdf.cell(50, 5, "Matriz / Fruta", 1, 0, "C")
            pdf.cell(25, 5, "Tiempo (min)", 1, 0, "C")
            pdf.cell(35, 5, "Conc. Con Agit.", 1, 0, "C")
            pdf.cell(35, 5, "Conc. Sin Agit.", 1, 0, "C")
            pdf.cell(35, 5, "Efecto (%)", 1, 1, "C")
            
            pdf.set_font("Arial", "", 8)
            for etp in efecto_por_tiempo_pdf:
                pdf.cell(50, 5, f"{etp['Matriz / Fruta']}", 1, 0, "L")
                pdf.cell(25, 5, f"{etp['Tiempo (min)']}", 1, 0, "C")
                pdf.cell(35, 5, f"{etp['Conc. Con Agit. (g/L)']}", 1, 0, "C")
                pdf.cell(35, 5, f"{etp['Conc. Sin Agit. (g/L)']}", 1, 0, "C")
                pdf.cell(35, 5, f"{etp['Efecto de Agitación (%)']}", 1, 1, "C")
            pdf.ln(4)

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

    # 5. Gráfico de Extracción Relativa Corregida
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
    ax_er_temp.legend(fontsize=7, bbox_to_anchor=(1.05, 1), loc="upper left")

    img_er_tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
    plt.savefig(img_er_tmp.name, bbox_inches="tight", dpi=150)
    plt.close(fig_er_temp)

    pdf.image(img_er_tmp.name, x=15, y=pdf.get_y() + 2, w=170)
    pdf.ln(5)

    # 6. Gráfica Global
    pdf.add_page()
    pdf.set_font("Arial", "B", 10)
    pdf.cell(0, 6, "6. Grafica Comparativa Global:", ln=True)
    pdf.ln(2)
    
    fig_temp, ax_temp = plt.subplots(figsize=(7, 4))
    for grupo, d in datos_agrupados.items():
        ax_temp.errorbar(
            d["Tiempos"],
            d["ConcProm"],
            yerr=d["ConcStd"],
            marker="o",
            capsize=3,
            label=grupo,
        )
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
            
            c_ultimo = concentracion[-1] if len(concentracion) > 0 and concentracion else 1.0
