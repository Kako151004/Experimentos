import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import linregress

# Configuración de la página
st.set_page_config(page_title="Diálisis", page_icon="🧪", layout="wide")

st.title("🧪 Simulador y Analizador: Cinética de Diálisis por Membrana")
st.write("Herramienta interactiva para el procesamiento de datos experimentales de transferencia de masa.")

# --- BARRA LATERAL: PARÁMETROS Y CALIBRACIÓN ---
st.sidebar.header("1. Parámetros del Sistema")
volumen = st.sidebar.number_input("Volumen del medio externo (mL):", value=120.0, step=10.0)
masa = st.sidebar.number_input("Masa de matriz vegetal (g):", value=12.0, step=1.0)

tiempos_input = st.sidebar.text_input(
    "Tiempos de muestreo (separados por espacios):", 
    value="0 5 10 15 20 30 45 60"
)
try:
    tiempo = np.array([float(x) for x in tiempos_input.split()])
except ValueError:
    st.sidebar.error("Por favor, ingresa los tiempos correctamente separados por espacios.")
    tiempo = np.array([])

st.sidebar.header("2. Curva de Calibrado (DNS)")
conc_e_input = st.sidebar.text_input(
    "Concentraciones estándar (g/L):", 
    value="0.2 0.4 0.6 0.8 1.0 1.2 1.4"
)
abs_e_input = st.sidebar.text_input(
    "Absorbancias estándar correspondientes:", 
    value="0.118 0.218 0.308 0.410 0.512 0.660 0.755"
)

try:
    concentracion_e = np.array([float(x) for x in conc_e_input.split()])
    abs_estandars = np.array([float(x) for x in abs_e_input.split()])
    
    # Regresión lineal: X = Concentración, Y = Absorbencia
    m, b, r, _, _ = linregress(concentracion_e, abs_estandars)
    r2 = r**2
except Exception:
    st.sidebar.error("Error en el formato de los datos estándar. Verifica que sean solo números separados por espacios.")
    m, b, r2 = 1.0, 0.0, 0.0

# --- PANEL PRINCIPAL: MOSTRAR CURVA DE CALIBRADO ---
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📊 Curva de Calibrado")
    fig_cal, ax_cal = plt.subplots(figsize=(6, 4))
    ax_cal.scatter(concentracion_e, abs_estandars, color='blue', label='Datos Estándar')
    ax_cal.plot(concentracion_e, m * concentracion_e + b, color='red', label=f'Regresión: y = {m:.4f}x + {b:.4f}')
    ax_cal.set_xlabel('Concentración (g/L)')
    ax_cal.set_ylabel('Absorbancia 600 nm')
    ax_cal.set_title('Curva de Calibrado DNS')
    ax_cal.grid(True)
    ax_cal.legend()
    st.pyplot(fig_cal)

with col2:
    st.subheader("📈 Parámetros de la Recta")
    st.metric(label="Pendiente (m)", value=f"{m:.4f}")
    st.metric(label="Intercepto (b)", value=f"{b:.4f}")
    st.metric(label="Coeficiente de Correlación (R²)", value=f"{r2:.4f}")
    st.info( fórmula de interpolación utilizada: $C = \\frac{\\text{ABS} - b}{m}$ )

st.markdown("---")

# --- BLOQUE EXPERIMENTAL (GESTIÓN DE HISTORIAL EN SESSION_STATE) ---
if 'historial' not in st.session_state:
    st.session_state['historial'] = []

st.subheader("🔬 Registro de Datos Experimentales")

with st.form(key="experimental_form"):
    c_cond1, c_cond2 = st.columns(2)
    with c_cond1:
        tipo_agitacion = st.radio("Condición del ensayo:", ("Con agitación", "Sin agitación"))
    with c_cond2:
        rpm = 0
        if tipo_agitacion == "Con agitación":
            rpm = st.number_input("Revoluciones por minuto (RPM):", value=100.0, step=10.0)
            etiqueta_rpm = f"{rpm} RPM"
        else:
            etiqueta_rpm = "Estático (0 RPM)"

    abs_exp_input = st.text_input(
        "Introduce las absorbancias experimentales para cada tiempo (separadas por espacios):",
        value="0.020 0.103 0.146 0.271 0.275 0.418 0.533 0.688" if tipo_agitacion == "Con agitación" else "0.025 0.042 0.075 0.079 0.106 0.127 0.206 0.241"
    )
    
    submit_button = st.form_submit_button(label="Registrar y Calcular Ensayo")

if submit_button:
    try:
        abs_experimental = np.array([float(x) for x in abs_exp_input.split()])
        if len(abs_experimental) != len(tiempo):
            st.error(f"La cantidad de valores de absorbancia ({len(abs_experimental)}) no coincide con la cantidad de tiempos ({len(tiempo)}).")
        else:
            # Cálculo de la concentración despejando de la recta y = mx + b
            concentracion_exp = (abs_experimental - b) / m
            
            # Guardar en el historial de Streamlit
            st.session_state['historial'].append({
                'RPM': etiqueta_rpm,
                'Tiempo': tiempo,
                'Abs': abs_experimental,
                'Conc': concentracion_exp
            })
            st.success(f"¡Ensayo ({etiqueta_rpm}) registrado con éxito!")
    except ValueError:
        st.error("Asegúrate de ingresar valores numéricos válidos en las absorbancias.")

# --- VISUALIZACIÓN DE RESULTADOS Y COMPARATIVA ---
if len(st.session_state['historial']) > 0:
    st.markdown("---")
    st.subheader("📋 Resultados Almacenados y Gráfica Comparativa")
    
    # Botón para limpiar historial
    if st.button("Limpiar Historial de Ensayos"):
        st.session_state['historial'] = []
        st.rerun()

    fig_comp, ax_comp = plt.subplots(figsize=(8, 5))
    
    for item in st.session_state['historial']:
        cond = item['RPM']
        t_vals = item['Tiempo']
        c_vals = item['Conc']
        
        # Mostrar tabla individual por cada ensayo registrado
        st.write(f"**Condición: {cond}**")
        tabla_datos = {
            "Tiempo (min)": t_vals,
            "ABS 600 nm": item['Abs'],
            "Concentración (g/L)": c_vals
        }
        st.dataframe(tabla_datos)
        
        # Trazar en el gráfico global comparativo
        ax_comp.plot(t_vals, c_vals, marker='o', linewidth=2, label=f"Condición: {cond}")

    ax_comp.set_xlabel("Tiempo (min)")
    ax_comp.set_ylabel("Concentración de azúcares (g/L)")
    ax_comp.set_title("Cinética de Difusión de Azúcares Reductores")
    ax_comp.grid(True)
    ax_comp.legend()
    
    st.pyplot(fig_comp)