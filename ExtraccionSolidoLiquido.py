# --- FUNCIÓN PARA GENERAR EL PDF COMPLETO ---
    def generar_pdf_informe(datos_agrupados, m, b, r2, volumen_agua, masa_fruta, efecto_agitacion_datos):
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
            
        # 3. Análisis de Efecto de Agitación (si existe)
        if len(efecto_agitacion_datos) > 0:
            pdf.add_page()
            pdf.set_font("Arial", "B", 10)
            pdf.cell(0, 6, "3. Analisis del Efecto de la Agitacion:", ln=True)
            
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

        # 4. Incluir Gráfica Global en el PDF
        pdf.add_page()
        pdf.set_font("Arial", "B", 10)
        pdf.cell(0, 6, "4. Grafica Comparativa Global:", ln=True)
        pdf.ln(2)
        
        # Generar imagen temporal de la gráfica global
        fig_temp, ax_temp = plt.subplots(figsize=(7, 4))
        for grupo, d in datos_agrupados.items():
            ax_temp.errorbar(d["Tiempos"], d["ConcProm"], yerr=d["ConcStd"], marker="o", capsize=3, label=grupo)
        ax_temp.set_xlabel("Tiempo (min)")
        ax_temp.set_ylabel("Concentracion (g/L)")
        ax_temp.set_title("Cinetica de Extraccion Global")
        ax_temp.grid(True)
        ax_temp.legend(fontsize=8)
        
        img_tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
        plt.savefig(img_tmp.name, bbox_inches="tight", dpi=150)
        plt.close(fig_temp)
        
        pdf.image(img_tmp.name, x=15, y=pdf.get_y() + 2, w=180)
        
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
        pdf.output(tmp.name)
        return tmp.name

    # Botón de Descarga actualizado en la barra lateral
    st.sidebar.markdown("---")
    st.sidebar.subheader("📄 Descarga de Informe")
    try:
        # Calcular de nuevo los datos de agitación para pasarlos al PDF
        frutas_base = set([g.split(" - ")[0] for g in grupos_unicos if " - " in g])
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

        ruta_pdf = generar_pdf_informe(datos_agrupados, m, b, r2, volumen_agua, masa_fruta, efecto_agitacion_datos_pdf)
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
