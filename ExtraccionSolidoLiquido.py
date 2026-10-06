from collections import defaultdict
import tempfile
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from fpdf import FPDF

# ==========================================
# --- 1. SIMULACIÓN O CARGA DE DATOS ---
# ==========================================
# (Asegúrate de ajustar esta parte con tu DataFrame real o tu fuente de datos)
# Ejemplo de datos simulados con 24 tiempos de muestreo:
tiempo_muestreo = np.linspace(0, 120, 24)  # 24 puntos desde 0 hasta 120 minutos
frutas_base = ["Tomate", "Manzana"]
condiciones = ["Tomate - Con Agitación", "Tomate - Sin Agitación"]

# Datos de calibración de ejemplo
m = 0.8542
b = 0.0215
r2 = 0.9981
volumen_agua = 0.5  # Litros
masa_fruta = 25.0  # Gramos

datos_agrupados = {}
for cond in condiciones:
  # Simulamos valores crecientes de absorbancia con 3 réplicas
  abs_base = 1.2 * (1 - np.exp(-tiempo_muestreo / 30))
  replicas = []
  for _ in range(3):
    ruido = np.random.normal(0, 0.02, len(tiempo_muestreo))
    replicas.append(np.clip(abs_base + ruido, 0.01, 2.5))

  replicas_arr = np.array(replicas)
  abs_prom = np.mean(replicas_arr, axis=0)
  abs_std = np.std(replicas_arr, axis=0, ddof=1)

  conc_prom = (abs_prom - b) / m
  conc_std = abs_std / m
  cv = (abs_std / abs_prom) * 100

  # Masas y rendimientos
  masa_prom = conc_prom * volumen_agua
  ext_prom = (masa_prom / masa_fruta) * 100
  rend_prom = ext_prom  # Ejemplo

  # Velocidades promedio por intervalos
  vel_prom = []
  for i in range(len(tiempo_muestreo) - 1):
    dt = tiempo_muestreo[i + 1] - tiempo_muestreo[i]
    dc = conc_prom[i + 1] - conc_prom[i]
    vel_prom.append(dc / dt if dt > 0 else 0)

  datos_agrupados[cond] = {
      "Corridas": replicas,
      "Tiempos": tiempo_muestreo,
      "AbsProm": abs_prom,
      "AbsStd": abs_std,
      "ConcProm": conc_prom,
      "ConcStd": conc_std,
      "CV": cv,
      "MasaProm": masa_prom,
      "ExtProm": ext_prom,
      "RendProm": rend_prom,
      "VelocidadPromedio": vel_prom,
  }

# Datos de efecto de agitación simulados
efecto_agitacion_datos = [{
    "Matriz / Fruta": "Tomate",
    "Conc. Final Con Agit. (g/L)": f"{datos_agrupados['Tomate - Con Agitación']['ConcProm'][-1]:.2f}",
    "Conc. Final Sin Agit. (g/L)": f"{datos_agrupados['Tomate - Sin Agitación']['ConcProm'][-1]:.2f}",
    "Diferencia Absoluta (g/L)": f"{(datos_agrupados['Tomate - Con Agitación']['ConcProm'][-1] - datos_agrupados['Tomate - Sin Agitación']['ConcProm'][-1]):.2f}",
    "Efecto Porcentual Agitación (%)": "12.4%",
}]


# ==========================================
# --- 2. FUNCIÓN PARA GENERAR EL PDF COMPLETO ---
# ==========================================
def generar_pdf_informe(
    datos_agrupados,
    m,
    b,
    r2,
    volumen_agua,
    masa_fruta,
    efecto_agitacion_datos,
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

  # 1. Parámetros Generales y Calibración
  pdf.set_font("Arial", "B", 10)
  pdf.cell(0, 6, "1. Parametros Generales y Calibracion:", ln=True)
  pdf.set_font("Arial", "", 9)
  pdf.cell(
      0,
      5,
      f"- Volumen de agua: {volumen_agua:.3f} L | Masa de fruta: {masa_fruta:.2f}"
      " g",
      ln=True,
  )
  pdf.cell(
      0,
      5,
      f"- Curva de Calibrado: y = {m:.4f}x + {b:.4f}  (R2 = {r2:.4f})",
      ln=True,
  )
  pdf.ln(4)

  # 2. Resultados Estadísticos por Condición (Con control de paginación para 24 datos)
  pdf.set_font("Arial", "B", 10)
  pdf.cell(
      0,
      6,
      "2. Resultados Estadisticos por Condicion (Absorbancia y"
      " Concentracion):",
      ln=True,
  )
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
      pdf.cell(12, 5, f"{t:.1f}", 1, 0, "C")
      pdf.cell(32, 5, abs_str, 1, 0, "C")
      pdf.cell(24, 5, f"{d['ConcProm'][i]:.2f}", 1, 0, "C")
      pdf.cell(18, 5, f"{d['ConcStd'][i]:.2f}", 1, 0, "C")
      pdf.cell(18, 5, f"{d['CV'][i]:.1f}%", 1, 0, "C")
      pdf.cell(24, 5, f"{d['MasaProm'][i]:.2f}", 1, 0, "C")
      pdf.cell(25, 5, f"{d['ExtProm'][i]:.1f}%", 1, 0, "C")
      pdf.cell(24, 5, f"{d['RendProm'][i]:.2f}%", 1, 1, "C")
    pdf.ln(5)

  # 3. Velocidades Promedio por Intervalos y Gráfico de Barras
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
      for ti, tf, vm in zip(
          tiempo_muestreo[:-1], tiempo_muestreo[1:], d["VelocidadPromedio"]
      ):
        if pdf.get_y() > 275:
          pdf.add_page()
        pdf.cell(50, 5, f"{ti:.1f} a {tf:.1f}", 1, 0, "C")
        pdf.cell(70, 5, f"{vm:.4f}", 1, 1, "C")
      pdf.ln(3)

    # Gráfico de Velocidades en página nueva limpia
    pdf.add_page()
    pdf.set_font("Arial", "B", 11)
    pdf.cell(0, 8, "Grafico de Velocidades Promedio de Extraccion", ln=True)
    pdf.ln(3)

    num_intervalos = len(tiempo_muestreo) - 1
    x = np.arange(num_intervalos)
    ancho = min(0.2, 0.8 / max(len(datos_agrupados), 1))

    fig_bar_temp, ax_bar_temp = plt.subplots(figsize=(8, 4))
    for i, (grupo, d) in enumerate(datos_agrupados.items()):
      ax_bar_temp.bar(
          x + (i * ancho), d["VelocidadPromedio"], width=ancho, label=grupo
      )

    labels_intervalos = [
        f"{tiempo_muestreo[j]:.1f}-{tiempo_muestreo[j+1]:.1f}m"
        for j in range(num_intervalos)
    ]
    ax_bar_temp.set_xlabel("Intervalos de Tiempo")
    ax_bar_temp.set_ylabel("Velocidad ((g/L)/min)")
    ax_bar_temp.set_title("Velocidades Promedio de Extraccion")
    ax_bar_temp.set_xticks(x + ancho * (len(datos_agrupados) - 1) / 2)
    ax_bar_temp.set_xticklabels(labels_intervalos, fontsize=6, rotation=45)
    ax_bar_temp.grid(True, axis="y")
    ax_bar_temp.legend(fontsize=7)

    img_bar_tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
    plt.savefig(img_bar_tmp.name, bbox_inches="tight", dpi=150)
    plt.close(fig_bar_temp)

    pdf.image(img_bar_tmp.name, x=15, y=pdf.get_y() + 2, w=180)
    pdf.ln(5)

  # 4. Análisis de Efecto de Agitación
  if len(efecto_agitacion_datos) > 0:
    pdf.add_page()
    pdf.set_font("Arial", "B", 11)
    pdf.cell(0, 8, "4. Analisis del Efecto de la Agitacion", ln=True)
    pdf.ln(2)

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

    # Gráfico de Diferencia de ABS en página nueva
    pdf.add_page()
    pdf.set_font("Arial", "B", 11)
    pdf.cell(
        0, 8, "Grafico de Diferencia de ABS (delta ABS) vs Tiempo", ln=True
    )
    pdf.ln(3)

    fig_dabs_temp, ax_dabs_temp = plt.subplots(figsize=(8, 4))
    for fruta in frutas_base:
      cond_con = f"{fruta} - Con Agitación"
      cond_sin = f"{fruta} - Sin Agitación"
      if cond_con in datos_agrupados and cond_sin in datos_agrupados:
        abs_con = datos_agrupados[cond_con]["AbsProm"]
        abs_sin = datos_agrupados[cond_sin]["AbsProm"]
        dif_abs_t = abs_con - abs_sin
        ax_dabs_temp.plot(tiempo_muestreo, dif_abs_t, marker="o", label=fruta)

    ax_dabs_temp.set_xlabel("Tiempo (min)")
    ax_dabs_temp.set_ylabel("Diferencia de ABS (Con - Sin)")
    ax_dabs_temp.set_title("Evolución Temporal de la Diferencia de Absorbancia")
    ax_dabs_temp.grid(True)
    ax_dabs_temp.legend(fontsize=7)

    img_dabs_tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
    plt.savefig(img_dabs_tmp.name, bbox_inches="tight", dpi=150)
    plt.close(fig_dabs_temp)

    pdf.image(img_dabs_tmp.name, x=15, y=pdf.get_y() + 2, w=180)
    pdf.ln(5)

  # 5. Extracción Relativa Corregida (Erel %)
  pdf.add_page()
  pdf.set_font("Arial", "B", 11)
  pdf.cell(
      0, 8, "5. Extraccion Relativa Corregida (Erel %) y Rendimiento", ln=True
  )
  pdf.ln(3)

  fig_er_temp, ax_er_temp = plt.subplots(figsize=(8, 4.5))
  for grupo, d in datos_agrupados.items():
    ax_er_temp.plot(tiempo_muestreo, d["ExtProm"], marker="o", label=grupo)
  ax_er_temp.set_xlabel("Tiempo (min)")
  ax_er_temp.set_ylabel("Extracción Relativa Corregida Erel (%)")
  ax_er_temp.set_title("Cinética de Extracción Relativa Normalizada")
  ax_er_temp.grid(True)
  ax_er_temp.legend(
      fontsize=7, bbox_to_anchor=(1.05, 1), loc="upper left"
  )

  img_er_tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
  plt.savefig(img_er_tmp.name, bbox_inches="tight", dpi=150)
  plt.close(fig_er_temp)

  pdf.image(img_er_tmp.name, x=15, y=pdf.get_y() + 2, w=170)
  pdf.ln(5)

  # 6. Gráfica Global Comparativa
  pdf.add_page()
  pdf.set_font("Arial", "B", 11)
  pdf.cell(0, 8, "6. Grafica Comparativa Global", ln=True)
  pdf.ln(3)

  fig_temp2, ax_temp2 = plt.subplots(figsize=(8, 4.5))
  for grupo, d in datos_agrupados.items():
    ax_temp2.errorbar(
        d["Tiempos"],
        d["ConcProm"],
        yerr=d["ConcStd"],
        marker="o",
        capsize=3,
        label=grupo,
    )
  ax_temp2.set_xlabel("Tiempo (min)")
  ax_temp2.set_ylabel("Concentracion (g/L)")
  ax_temp2.set_title("Cinetica de Extraccion Global")
  ax_temp2.grid(True)
  ax_temp2.legend(
      fontsize=7, bbox_to_anchor=(1.05, 1), loc="upper left"
  )

  img_tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
  plt.savefig(img_tmp_file.name, bbox_inches="tight", dpi=150)
  plt.close(fig_temp2)

  pdf.image(img_tmp_file.name, x=15, y=pdf.get_y() + 2, w=170)

  tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
  pdf.output(tmp.name)
  return tmp.name


# ==========================================
# --- 3. EJECUCIÓN DE PRUEBA ---
# ==========================================
pdf_path = generar_pdf_informe(
    datos_agrupados,
    m,
    b,
    r2,
    volumen_agua,
    masa_fruta,
    efecto_agitacion_datos,
    tiempo_muestreo,
    frutas_base,
)
print(f"PDF generado exitosamente en: {pdf_path}")
