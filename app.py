from appFolder.inicioPage import set_main_page
from appFolder.alcancePage import set_alcance_page
from appFolder.config import set_config, init_sidebar
from appFolder.Funcionalidades.medicina_precision import set_medicina_precision_page
from appFolder.Funcionalidades.indicaciones_farmaco import set_indicaciones_farmaco_page
from appFolder.Funcionalidades.indicaciones_genotipo import set_indicaciones_genotipo_page


set_config()
ventana = init_sidebar()

# LATERAL OPCIÓN 1: INICIO
if ventana == "Inicio":
    set_main_page()

# LATERAL OPCIÓN 2: Alcance
if ventana == 'Alcance':
    set_alcance_page()

# LATERAL OPCIÓN 3
if ventana == 'Indicaciones PGx por Fármaco':
    set_indicaciones_farmaco_page()

# LATERAL OPCIÓN 4
if ventana == 'Indicaciones basadas en el Genotipo del Paciente':
    set_indicaciones_genotipo_page()

# LATERAL OPCIÓN 5
if ventana == 'Medicina de Precisión':
    set_medicina_precision_page()
