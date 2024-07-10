import streamlit as st
import matplotlib.pyplot as plt
from app_funciones_inicio import estadisticas, circle

# Definir la página de inicio de la aplicación


def set_main_page():
    """Definir la página de inicio de la aplicación"""
    st.header(f'BIENVENIDO A Drug4Me! :dna: :pill:')
    st.markdown("En **Drug4Me** estamos comprometidos a impulsar **tratamientos personalizados** para optimizar la "
                "experiencia de cada paciente. Nuestra plataforma ayuda en la prescripción segura de farmácos, "
                "asegurando así un tratamiento óptimo y adaptado a las necesidades únicas de cada invididuo.")

    st.markdown("")
    st.markdown("##### :pushpin: **DATOS CLAVE**")
    st.markdown("- La FDA señala que las ADRs pueden llegar a costar <span style='color:  red;'><b> 136 billones de "
                "dolares </b></span>  y alrededor de <span style='color: red ;'><b>106.000 muertes</b></span> al año.",
                unsafe_allow_html=True)
    st.markdown("- En España, en un periodo de 5 años, se registraron  <span style='color:  red;'><b>350.835 "
                "hospitalizaciones</b></span> por ADRs, <span style='color: red;'><b>1,69%</b></span> de todos los"
                " ingresos hospitalarios agudos. ", unsafe_allow_html=True)
    st.markdown("**Queremos contribuir a reducir las ADRs, mejorar la seguridad en la prescipción de medicamentos "
                "y la calidad de vida de nuestros pacientes.**")

    st.markdown("")
    st.markdown("##### :pushpin: **ESTADÍSTICAS DE NUESTRA BASE DE DATOS**")
    num_farmacos, num_clinan, num1a, num1b, num2a, num2b, num3, num4, ddi, mayor, moderate, minor, unkown, allele \
        = estadisticas()

    col1, col2, col3 = st.columns([5, 5, 5.5])
    with col1:
        circle_farmacos = circle(110, num_farmacos, "&nbsp;&nbsp;&nbsp;FÁRMACOS<br> AUTORIZADOS")
        st.markdown(circle_farmacos, unsafe_allow_html=True)

    with col2:
        var_farm = circle(60, f"+ {num_clinan}", "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"
                                                 "&nbsp;&nbsp;&nbsp;INTERACCIONES<br>VARIANTE GENÉTICA-FÁRMACO")
        st.markdown(var_farm, unsafe_allow_html=True)
    with col3:
        pie_chart = {"labels": ["Nivel 1", "Nivel 2", "Nivel 3", "Nivel 4"],
                     "sizes": [num1a + num1b, num2a + num2b, num3, num4], "explode": [0.1, 0, 0, 0],
                     "colors": ["green", "blue", 'orange', 'red']}
        fig1, ax1 = plt.subplots()
        ax1.pie(pie_chart["sizes"], labels=pie_chart["labels"], autopct='%1.1f%%', explode=pie_chart["explode"],
                startangle=90, labeldistance=1.1, textprops={'fontsize': 14}, pctdistance=0.6, radius=0.5,
                colors=pie_chart["colors"])
        ax1.set_aspect('equal', adjustable="datalim")  # Equal aspect ratio ensures that pie is drawn as a circle.
        ax1.set_title("Niveles de Evidencia \nvariante genética-fármaco:", fontsize=16, color='#3498db', weight='bold')
        st.pyplot(fig1)

    col1, col2, col3 = st.columns([5, 5, 5.5])
    with col1:
        num_ddi = circle(75, allele, "ANOTACIONES BASADAS<br>EN ALELOS/GENOTIPOS")
        st.markdown(num_ddi, unsafe_allow_html=True)
    with col2:
        num_ddi = circle(90, ddi, "&nbsp;&nbsp;&nbsp;&nbsp;INTERACCIONES <br>FÁRMACO-FÁRMACO")
        st.markdown(num_ddi, unsafe_allow_html=True)
    with col3:
        pie_chart = {"labels": ["Mayor", "Moderate", "Minor", "Unkown"],
                     "sizes": [mayor, moderate, minor, unkown], "explode": [0.1, 0, 0, 0],
                     "colors": ['red', 'orange', 'green', 'gray', ]}
        fig1, ax1 = plt.subplots()
        ax1.pie(pie_chart["sizes"], labels=pie_chart["labels"], autopct='%1.1f%%', explode=pie_chart["explode"],
                startangle=90, labeldistance=1.1, textprops={'fontsize': 14}, pctdistance=0.6, radius=0.5,
                colors=pie_chart["colors"])
        ax1.set_aspect('equal', adjustable="datalim")  # Equal aspect ratio ensures that pie is drawn as a circle.
        ax1.set_title("Niveles de Gravedad \nfármaco-fármaco:", fontsize=16, color='#3498db', weight='bold')
        st.pyplot(fig1)

    st.markdown("##### :pushpin: **¿CÓMO FUNCIONA?**")
    st.markdown(":arrow_right: **Inicio de la Aplicación:**")
    st.markdown("""<div style="margin-left: 30px;">
                    <ul style="margin-bottom: 15px; margin-top: -10px;">
                        <div> 1.- Si la base de datos no está creada, seguir los pasos indicados en <b>Actualización de 
                        la Base de Datos</b>. </div>
                        <div> 2.- Si ya está creada, para abrir la aplicación ejecutar el comando: 
                        <b>streamlit run app.py</b></div>
                    </div>
                </div>
                </ul>""", unsafe_allow_html=True)

    st.markdown(":arrow_right: **Actualización de la Base de Datos:**")
    st.markdown("""    
        <div style="margin-left: 30px;"> 
            <ul style="margin-bottom:15px; margin-top: -10px;">
                <div>1.- Si la conexión se encuentra en la red de Vicomtech, se debe cambiar a otra red.</div>
                <div>2.- En caso de que la aplicación esté abierta, cerrarla.</div>
                <div>3.- Ejecutar el comando: <b>python .\\create_new_db.py</b>.</div>
                <div>4.- Esperar a que termine de ejecutar y volver a abrir la aplicación.</div>
        </div>
    </ul>
    """, unsafe_allow_html=True)

    st.markdown(":arrow_right: **Funcionalidades:**")
    st.markdown("""
        <div style="margin-left: 30px;">
            <div style="margin-bottom: 5px; font-weight: bold;margin-top: -10px;">
                1.- Obtener indicaciones PGx por fármaco.
            </div>
            <ul style="margin-bottom: 5px;">
                <li>Introducir el nombre del <b>principio activo en castellano</b> para el que se quieren obtener las 
                indicaciones.</li>
                <li>Seleccionar el fármaco deseado entre aquellos que contienen este principio activo, incluidos los 
                medicamentos concomitantes.</li>
                <li>Resultados: 
                    <ul>
                        <li>Asociaciones entre el fármaco y variantes genéticas. Indicaciones a tres niveles: 
                         PharmGKB (EEUU), EMA (Europa) y el Panel Genético (España).</li>
                        <li>Asociaciones entre el fármaco y otros fármacos. Indicaciones según la base de datos
                         DDinter (China) y los prospectos de los medicamentos de la EMA.</li>
                    </ul>
                </li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    st.write("")
    st.markdown("""
    <div style="margin-left: 30px;">
                <div style="margin-bottom: 5px; font-weight: bold;">
                    2.- Obtener indicaciones PGx basadas en el Genotipo del Paciente.
                </div>
                <ul style="margin-bottom: 5px;">
                    <li>Introducir el <b>id del paciente (paciente+número)</b>.</li>
                    <li>Se analiza el correspondiente  archivo VCF, obteniendo su perfil genético y su genotipo.</li>
                    <li>Resultados: 
                        <ul>
                            <li>Asociaciones con fármacos e indicaciones PGx en base a las variantes genéticas y el 
                            genotipo que presenta.</li>
                        </ul>
            """, unsafe_allow_html=True)
    st.write("")
    st.markdown("""
    <div style="margin-left: 30px;">
                <div style="margin-bottom: 5px; font-weight: bold;">
                    3.- Medicina de Precisión: Obtener indicaciones PGx basadas en el perfil genético de un paciente 
                    y el fármaco que se pretende recetar a ese paciente.
                </div>
                <ul style="margin-bottom: 5px;">
                    <li>Introducir el <b>id del paciente (paciente+número)</b>.</li>
                    <li>Introducir el nombre del <b>principio activo en castellano</b> para el que se quieren obtener 
                    las indicaciones.
                        <ul>
                            <li>Seleccionar el fármaco deseado entre aquellos que contienen este principio
                             activo, incluidos los medicamentos concomitantes.</li>
                        </ul>
                </li>
                <li>Si es el caso, introducir <b>los fármacos que toma el paciente actualmente</b>.</li>
                <li>Resultados:
            <ul>
                <li>Asociaciones entre las variantes genéticas del paciente y el fármaco a recetar:
                    <ul>
                        <li>Indicaciones PGx en base a las variantes genéticas y el genotipo que presenta.</li>
                    </ul>
                </li>
                <li>Asociaciones entre fármacos:
                    <ul>
                        <li>Asociaciones entre los fármacos que toma el paciente y el fármaco a recetar.</li>
                        <li>Asociaciones entre el fármaco a recetar y otros fármacos.</li>
                    </ul>
                </li>
            </ul>
        </li>
    </ul>""", unsafe_allow_html=True)

    st.divider()
    st.markdown(":red[**RECUERDA:**]")
    st.markdown("""<ul style="margin-bottom: 5px;">
               <li>Utiliza esta herramienta como apoyo para optimizar el tramiento, pero no como sustituto 
               de la valoración clinica del médico.</li>
               <li>La decisión final sobre la prescripción de medicamentos siempre debe ser tomada por un 
               médico, quien considerará todos los aspectos clínicos y características individuales del 
               paciente.</li>
           </ul>""", unsafe_allow_html=True)
