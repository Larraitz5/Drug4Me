import streamlit as st

# Definir la página de alcance de la aplicación


def set_alcance_page():
    """Definir la página de alcance de la aplicación"""
    st.markdown("##### :pushpin: **BASES DE DATOS**")
    st.markdown("Nuestra aplicación integra datos de fuentes nacionales como internacionales.")
    st.markdown("- Se basa principalmente en la base de datos de fármacos del "
                "**[CIMA](https://cima.aemps.es/cima/publico/nomenclator.html)** (Centro de Información de "
                "Medicamentos de la Agencia Española de Medicamentos y Productos Sanitarios), por tanto considera "
                "medicamentos autorizados en España como punto de partida.")
    st.markdown("- **[El Catálogo de Pruebas Genéticas de España](https://cgen.sanidad.gob.es/#/consulta-general)**: "
                "Proporciona asociaciones gen-fármaco, y sus correspondientes observaciones. Dispone de pruebas "
                "genéticas y genómicas del Sistema Nacional de Salud (SNS) en el área de farmacogenómica. Estas "
                "pruebas son muy recientes y se encuentran en constate actualización. Sin embargo, no se presenta el "
                "nivel de evidencia de las pruebas y las recomendaciones terapéuticas son muy limitadas.")
    st.markdown("- **[EMA](https://www.ema.europa.eu/en/medicines)** (European Medicine Agency): Se obtienen "
                "indicaciones terapéuticas farmacogenómicas para los fármacos autorizados a nivel europeo.")
    st.markdown("- **[PharmGKB](https://www.pharmgkb.org/)**: Proporciona información sobre el efecto de las variantes"
                " genéticas en la respuesta de los medicamentos. Asimismo, anotaciones basadas en el genotipo. "
                " Utiliza diferentes fuentes para recopilar información, como: CPIC, FDA (U.S. Food and Drug "
                "Administration), DrugBank, EMA...")
    st.markdown("- **[DDInter](http://ddinter.scbdd.com/)**: Desarrollado en China, proporciona anotaciones de "
                "asociaciones entre fármacos.")
    st.markdown("- Se han añadido indicaciones de interacciones entre fármacos obtenidos a partir de los prospectos"
                " de los fármacos disponibles en la [EMA](https://www.ema.europa.eu/en/medicines).")
    st.markdown("")
    st.markdown("")
    st.markdown("##### :pushpin: **LIMITACIONES**")
    st.markdown("- **Posible perdida de información en el proceso de integración de los datos:** "
                "Aunque los nombres en inglés de los fármacos están respaldados por múltiples fuentes y "
                " códigos, es posible que algunos no se hayan traducido debido a la"
                " falta de correspondencia entre bases de datos o discrepancias tipográficas.  ")
    st.markdown("- **Interacciones farmacológicas limitadas:** La información sobre interacciones entre fármacos es "
                "limitada. Es por ello que se han extraido a partir de los prospectos de los fármacos disponibles en "
                "EMA. ")
    st.markdown("- **Procesamiento del archivo VCF:** El procesamiento de archivos VCF puede no ser óptimo"
                " en algunos casos y podría estar limitado a archivos pequeños con pocas variantes genéticas.")
    st.markdown("- Hasta el momento se cuenta con 4 archivos VCF para poder realizar simulaciones ("
                "paciente1, paciente2, paciente3, paciente4)")
