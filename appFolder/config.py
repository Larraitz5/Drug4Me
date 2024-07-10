import os
from PIL import Image
import streamlit as st

# Definir la configuración de la aplicación y la barra lateral


def set_config():
    """Definir la configuracion de la aplicación"""
    # Cargar la imagen
    im = Image.open(os.path.join(os.getcwd(), r'data/images/icon.png'))
    # Configurar el tema de la página con streamlit
    st.set_page_config(page_title="Drug4me", page_icon=im, layout="wide", initial_sidebar_state="expanded",
                       menu_items={'Get Help': 'https://www.extremelycoolapp.com/help',
                                   'Report a bug': "https://www.extremelycoolapp.com/bug",
                                   'About': "# This is a *valuable* cool appFolder!"})

    # Establecer el tema personalizado
    st.markdown("""<style>
        [data-testid=stSidebar] {
            background-color: hsl(210, 50%, 90%); 
        }</style>""", unsafe_allow_html=True)

    # Establecer el color de fondo personalizado para el campo de entrada de texto
    st.markdown("""
    <style>
        input[type="text"] {
            background-color: hsl(210, 50%, 90%); /* Color de fondo personalizado para el campo de texto */
        }
    </style>
    """, unsafe_allow_html=True)
    # Color para las opciones seleccionadas en multiselect
    st.markdown(
        """
    <style>
    span[data-baseweb="tag"] {
      background-color: hsl(210, 50%, 30%);
    }
    </style>
    """, unsafe_allow_html=True,)


def init_sidebar():
    """Definir la barra lateral de la aplicación"""
    with st.sidebar:
        st.markdown(f'# **Drug4Me** :dna: :pill:')
        # Crear un radio button para la sección principal
        dictionary = {"Inicio": [], "Alcance": [], "Funcionalidades": ['Indicaciones PGx por Fármaco',
                                                                       'Indicaciones basadas en el Genotipo del '
                                                                       'Paciente', 'Medicina de Precisión']}
        ventana = st.selectbox("Seleccione el apartado que desea:", dictionary, index=0)
        if ventana == "Funcionalidades":
            ventana = st.sidebar.radio("Elija una funcionalidad:", (dictionary["Funcionalidades"]))

    return ventana
