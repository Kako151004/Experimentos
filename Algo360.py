import math
import streamlit as st
import sympy as sp
st.set_page_config(
    page_title="Calculadora de Reynolds y Fluidos No-Newtonianos",
    page_icon="🧪",
    layout="wide",
)
# Título de la aplicación
st.title("Calculadora de Flujo y Factor de Fricción")
st.markdown(
    "Herramienta interactiva para el análisis de fluidos Newtonianos y No-Newtonianos."
)

# Menú desplegable para elegir el tipo de fluido (reemplaza al input "si/no")
tipo_fluido = st.selectbox(
    "Seleccione el tipo de fluido:", ["Newtoniano", "No-Newtoniano"]
)

st.divider()

# Sección para Fluidos Newtonianos
if tipo_fluido == "Newtoniano":
  st.subheader("Parámetros para Fluido Newtoniano")

  # Usamos columnas para ordenar la interfaz
  col1, col2 = st.columns(2)

  with col1:
    # Sliders combinados con cajas numéricas para precisión exacta
    densidad = st.number_input("Densidad (kg/m³)", value=1000.0, step=1.0)
    velocidad_media = st.number_input(
        "Velocidad media (m/s)", value=2.0, step=0.1
    )

  with col2:
    diametro_interno = st.number_input(
        "Diámetro interno (m)", value=0.05, step=0.001
    )
    viscosidad = st.number_input(
        "Viscosidad dinâmica (Pa·s o cP)", value=0.001, format="%.5f"
    )

  # Cálculo del Número de Reynolds
  if viscosidad > 0 and diametro_interno > 0:
    nre = ((densidad * diametro_interno * velocidad_media) * 100 // viscosidad) / 100

    st.markdown("---")
    st.subheader("Resultados")
    st.metric(label="Número de Reynolds ($N_{Re}$)", value=f"{nre:.2f}")

    if nre >= 4000:
      st.warning(
          "El flujo corresponde a un régimen **Turbulento**."
      )
      rugosidad_absoluta = st.number_input(
          "Rugosidad absoluta de la tubería (ε en metros):",
          value=0.0015,
          format="%.5f",
      )

      if rugosidad_absoluta > 0:
        rugosidad_relativa = rugosidad_absoluta / diametro_interno
        a1 = (5.74 / (nre**0.9)) + (rugosidad_relativa / 3.7)
        a2 = (math.log10(a1)) ** 2
        fd = 0.25 / a2
        st.success(
            f"**Factor de fricción de Darcy (fd):** `{fd:.5f}`"
        )

    elif nre <= 2100:
      fd = 64 / nre
      st.info(
          "El flujo corresponde a un régimen **Laminar**."
      )
      st.success(
          f"**Factor de fricción (fd):** `{fd:.5f}`"
      )

    else:
      st.error(
          "El flujo se encuentra en la **zona de transición**."
      )

# Sección para Fluidos No-Newtonianos
elif tipo_fluido == "No-Newtoniano":
  st.subheader("Parámetros para Fluido No-Newtoniano (Ley de Potencia)")

  col1, col2 = st.columns(2)

  with col1:
    densidad = st.number_input("Densidad (kg/m³)", value=1050.0, step=1.0)
    velocidad_media = st.number_input(
        "Velocidad media (m/s)", value=1.5, step=0.1
    )
    diametro_interno = st.number_input(
        "Diámetro interno (m)", value=0.04, step=0.001
    )

  with col2:
    indice_consistencia = st.number_input(
        "Índice de consistencia (k)", value=2.5, step=0.1
    )
    indice_comportamiento = st.number_input(
        "Índice de comportamiento (n)", value=0.6, step=0.05
    )

  if (
      indice_consistencia > 0
      and indice_comportamiento > 0
      and diametro_interno > 0
  ):
    # Reynolds general
    a1 = densidad * (velocidad_media ** (2 - indice_comportamiento)) * (
        diametro_interno**indice_comportamiento
    )
    a2 = indice_consistencia * (8 ** (indice_comportamiento - 1))
    a3 = ((4 * indice_comportamiento) / ((3 * indice_comportamiento) + 1)) ** (
        indice_comportamiento
    )
    nreg = (a1 / a2) * a3

    # Reynolds crítico
    b1 = 6464 * indice_comportamiento
    b2 = (1 + (3 * indice_comportamiento)) ** 2
    b3 = (2 + indice_comportamiento) / (1 + indice_comportamiento)
    nrec = (b1 * ((2 + indice_comportamiento) ** b3)) / b2

    st.markdown("---")
    st.subheader("Resultados")

    col_res1, col_res2 = st.columns(2)
    with col_res1:
      st.metric(
          label="Reynolds General ($N_{Re,G}$)", value=f"{nreg:.2f}"
      )
    with col_res2:
      st.metric(
          label="Reynolds Crítico ($N_{Re,C}$)", value=f"{nrec:.2f}"
      )

    if nreg < nrec:
      ff = 16 / nreg
      fd = 4 * ff
      st.info(
          "El flujo es **Laminar** (Reynolds general menor que el crítico)."
      )
      st.success(
          f"**Factor de fricción:** `{fd:.5f}`"
      )

    elif nreg > nreg:  # (Nota: aquí tu lógica original evaluaba nreg > nrec)
      pass

    elif nreg > nrec:
      st.warning(
          "El flujo es **Turbulento** (Calculando ecuación implícita con"
          " SymPy...)"
      )
      try:
        ff_sym = sp.symbols("ff")
        eq_a1 = (
            4 / (indice_comportamiento**0.75)
        ) * sp.log(nreg * (ff_sym ** (1 - (indice_comportamiento / 2))), 10) - (
            0.4 / (indice_comportamiento**1.2)
        )
        eq_a2 = ff_sym - (1 / eq_a1) ** 2
        ffr = sp.nsolve(eq_a2, ff_sym, 0.005)
        fd = 4 * float(ffr)
        st.success(
            f"**Factor de fricción:** `{fd:.5f}`"
        )
      except Exception as e:
        st.error(
            f"No se pudo resolver numéricamente para estos valores: {e}"
        )
