import os
import time
import re
import PyPDF2
import requests
import pandas as pd
from bs4 import BeautifulSoup
from db_funciones import read_json_file
from ddi_funciones_EMA import solicitud_downloadfile_url

# Funciones para el proceso de obtención de ddi a partir de los prospectos de la EMA
properties_ema = read_json_file("EMA_DDI/properties_ema/properties_ema.json")["ema"]


# Paso 1: Obtener el excel de todos los medicamento desde la EMA, procesarlo y filtrarlo
def df_data_ema():
    """ Procesa y filtra el archivo de fármacos de la EMA.
    Devuelve un DataFrame con todos los fármacos"""
    columns = properties_ema["db_columns"]
    # Leer data desde el Excel y convertir a un df, seleccionando las columnas de interés
    excel_file = properties_ema["file_path_medicines"]
    df_ema_medicines = pd.read_excel(excel_file, header=0, skiprows=8, usecols=columns)
    df_ema_medicines['Active substance'] = df_ema_medicines['Active substance'].str.upper()
    df_ema_medicines = df_ema_medicines.loc[df_ema_medicines['Category'] == "Human"]
    df_ema_medicines = df_ema_medicines.loc[df_ema_medicines['Authorisation status'] == "Authorised"]
    df_ema_medicines.columns = ["Category", "Medicine_name", "Therapeutic_area", "INN_common_name", "Active_substance",
                                "Authorisation_status", "ATC_code", "Condition_Indication", "URL"]
    return df_ema_medicines


def get_ema_data():
    """Descarga dinámica del archivo de fármacos desde el EMA y obtención del df con todos los fármacos."""
    solicitud_downloadfile_url(properties_ema["download_url"], properties_ema["file_path_medicines"])
    df_ema_medicines = df_data_ema()
    return df_ema_medicines


# Paso 2: Descargar y obtener prospectos mediante la URL.
def download_prosp(url, medicine_name, nombre_archivo):
    """Descarga el prospecto de un medicamento desde una URL y guarda el archivo localmente.
    Recibe 3 parámetros: la URL que contiene el prospecto (str), el nombre del medicamento (str), el nombre del
     archivo a guardar (txt).
    Devuelve una tupla que contiene el nombre del archivo guardado y el nombre del medicamento si la descarga
     fue exitosa, None si ocurrió algún error."""
    try:
        response = requests.get(url)
        if response.status_code == 200:
            # Obtener el contenido de la respuesta
            html_content = response.text

            # Crear un objeto BeautifulSoup para analizar el HTML
            soup = BeautifulSoup(html_content, 'html.parser')
            # Filtrar los links buscando textos clave
            links = soup.find_all('a', target="_blank",
                                  class_='standalone align-self-top d-inline-block mt-3-5 mt-md-0 flex-shrink-0')

            # Iterar sobre los enlaces encontrados para encontrar el PDF específico
            for link in links:
                try:
                    href = link.get('href', '')
                    if 'product-information' in href:
                        file_path_save = properties_ema["output_path_prospects"] + nombre_archivo
                        href_file = "https://www.ema.europa.eu" + href
                        descarga = solicitud_downloadfile_url(href_file, file_path_save)
                        if descarga is None:
                            return None, None
                        else:
                            return nombre_archivo, medicine_name
                except (Exception,) as e:
                    print(e)
                    continue
        else:
            print(f"Outside link - Status code: {response.status_code} - Retry after: {float(response.headers["Retry-After"])}")
            time.sleep(float(response.headers["Retry-After"]))
            response = requests.get(url, verify=False)
            # Verificar si la solicitud fue exitosa (código de estado 200)

            if response.status_code == 200:
                # Obtener el contenido de la respuesta
                html_content = response.text

                # Crear un objeto BeautifulSoup para analizar el HTML
                soup = BeautifulSoup(html_content, 'html.parser')
                # Filtrar los links buscando textos clave
                links = soup.find_all('a', target="_blank",
                                      class_='standalone align-self-top d-inline-block mt-3-5 mt-md-0 flex-shrink-0')

                # Iterar sobre los enlaces encontrados para encontrar el PDF específico
                for link in links:
                    try:
                        href = link.get('href', '')
                        if 'product-information' in href:
                            file_path_save = properties_ema["output_path_prospects"] + nombre_archivo
                            href_file = "https://www.ema.europa.eu" + href
                            descarga = solicitud_downloadfile_url(href_file, file_path_save)
                            if descarga is None:
                                return None, None
                            else:
                                return nombre_archivo, medicine_name
                    except (Exception,) as e:
                        print(e)
                        continue
            return None, None
    except (Exception,):
        return None, None


# Paso 3: Preprocesamiento del prospecto para obtener la sección 4.5.
def find_page(text_extracted, titles):
    """Encuentra el número de la página que contiene uno de los títulos dados en una lista.
    Recibe 2 parámetros: objeto que contiene el texto extraído de un documento, y una lista de títulos a buscar en el.
    Devuelve el número de página que contiene uno de los títulos si se encuentra, None si no se encuentra ninguno."""
    for page_num in range(len(text_extracted.pages)):
        page = (text_extracted.pages[page_num])
        text = page.extract_text()
        if any(title in text for title in titles):
            return page_num
    return None


def extract_text_pages(text_extracted, start_page, end_page):
    """Extrae el texto de las páginas indicadas de un documento.
    Recibe 3 parámetros: objeto que contiene el texto extraído de un documento, los números de la primera y última
    página a extraer.
    Devuelve el texto extraído de las páginas indicadas si se encontró, None si no se encuentró."""
    section_text = ''
    for page_num in range(start_page, end_page + 1):
        page = text_extracted.pages[page_num]
        text = str(page.extract_text())
        section_text += text
    if section_text != '':
        return section_text
    else:
        return None


def get_45_prospects_section(file_name_pdf, file_name_final_txt, medicine_name):
    """Extrae la sección 4.5 de un prospecto de medicamento.
    Recibe 3 parámetros: nombre del archivo PDF del prospecto, nombre del archivo preprocesado final y el nombre del
    medicamento.
    Devuelve una tupla que contiene el nombre del archivo preprocesado final y el nombre del mediccamento si la sección
    4.5 se extrajo correctamente, None si no se pudo extraer.
    """
    output_path_prospects = properties_ema["output_path_prospects"]
    # Directorios donde guardar los prospectos preprocesados
    path_preprocesados = properties_ema["path_prospects_prepocesados"]
    path_no_preprocesados = properties_ema["path_prospects_no_prepocesados"]

    # Títulos de inicio (4.5) y fin (4.6)
    start_titles = ['Interaction with other', '4.5 Interaction with', '4.5 Inter', '4.5 I nterac', '4.5 \nInterac',
                    '4.5  Interac', '4.5 In', '4.5  Interaction']
    end_titles = ['Fertility, p regnancy and lactation', 'Fertility,', '4.6 Pregnancy', '4.6 Ferti', '4.6 Fe',
                  '4.6  Ferti']

    path_prospect = os.path.join(output_path_prospects, file_name_pdf)
    try:
        with (open(path_prospect, 'rb') as file):
            reader = PyPDF2.PdfReader(file)
            # Buscar las páginas de inicio(4.5) y fin(4.6)
            start_page_num = find_page(reader, start_titles)
            end_page_num = (find_page(reader, end_titles))

            if start_page_num is not None and end_page_num is not None:
                section_pages = extract_text_pages(reader, start_page_num, end_page_num)
                # Bsucar posiciones exactas y extraer texto desde 4.5 a 4.6
                posicion_inicio_4_5 = section_pages.find("4.5 ")
                posicion_fin_4_6 = section_pages.find("4.6 ")
                texto45_46 = section_pages[posicion_inicio_4_5:posicion_fin_4_6]

                # Procesar el texto mediante expresiones regulares:
                # Eliminar saltos de línea que están seguidos por letras o paréntesis.
                texto45_46 = re.sub(r'\n([A-Za-z(])', r'\1', texto45_46)
                # Insertar \n entre una minúscula seguida por una mayúscula
                texto45_46 = re.sub(r'([a-z])([A-Z])', r'\1 \n \2', texto45_46)

                # Nombre del archivo de salida preprocesado
                prospects_processed_path = os.path.join(path_preprocesados, file_name_final_txt)
                with open(prospects_processed_path, "w", encoding="utf-8") as archivo:
                    archivo.write(texto45_46)
                    return file_name_final_txt, medicine_name
            else:
                no_preprocesados_path = os.path.join(path_no_preprocesados, file_name_final_txt)
                os.replace(path_prospect, no_preprocesados_path)
                return None, None

    except (Exception,):
        no_preprocesados_path = os.path.join(path_no_preprocesados, file_name_final_txt)
        os.replace(path_prospect, no_preprocesados_path)
        return None, None


# Paso 4: Procesar la sección 4.5 para obtener ddi mediante la lista de fármacos y palabras clave
def buscar_interacciones(file_name_preproc_txt, file_name_ddi, pa, medicine_name, lista_farmacos, palabras_clave):
    """Busca interacciones entre fármacos en un texto preprocesado.
    Recibe 6 parámetros:
        - Nombre del archivo preprocesado
        - Nombre del archivo de salida con las interacciones (o sin).
        - El nombre del principio activo del medicamento
        - El nombre del medicamento
        - Lista de fármacos a buscar
        - Lista de palabras clave a buscar que indican interacciones
    Devuelve una lista de párrafos que contienen interacciones."""
    # Directorio del archivo preprocesado (donde buscar las ddi)
    output_path_prepocesados = properties_ema["path_prospects_prepocesados"]
    # Directorios donde guardar los prospectos con ddi y sin ddi
    path_ddi = properties_ema["path_ddi"]
    path_dii_no = properties_ema["path_ddi_no"]
    # Leer los preprocesados
    with open(os.path.join(output_path_prepocesados, file_name_preproc_txt), "r", encoding="utf-8") as archivo:
        texto = archivo.read()
        # Dividir el texto en párrafos
        parrafos = texto.split(' \n ')

        # Eliminar los pa y nombre del fármaco que estamos procesando:
        # Compilar patrones para buscar "pa" y el nombre (insensible a mayúsculas y minúsculas)
        patron_pa = re.compile(pa, re.IGNORECASE)
        patron_mn = re.compile(medicine_name, re.IGNORECASE)
        # Filtrar la lista de fármacos para eliminar los elementos que coincidan con el patrón de pa o nombre
        lista_farmacos = [farmaco for farmaco in lista_farmacos if not patron_pa.match(farmaco) or
                          patron_mn.match(farmaco)]

        # Para cada fármaco en la lista, crear un patrón de búsqueda
        # (tratar carácteres especiales y mayúsculs/minúsculas)
        patrones_farmacos = [re.compile(r'\b{}\b'.format(re.escape(farmaco)), re.IGNORECASE)
                             for farmaco in lista_farmacos]
        patrones_palabras = [re.compile(r'\b{}\b'.format(re.escape(palabra)), re.IGNORECASE)
                             for palabra in palabras_clave]

        interacciones = []
        contiene_interacciones = False
        # Para cada párrafo buscar si contiene alguno de los fármacos y palabras clave
        for parrafo in parrafos:
            contiene_farmaco = any(re.search(patron, parrafo) for patron in patrones_farmacos)
            contiene_palabra_clave = any(re.search(patron, parrafo) for patron in patrones_palabras)

            if contiene_farmaco and contiene_palabra_clave:
                contiene_interacciones = True

                for patron in patrones_farmacos:
                    # Las ocurrencias de los fármacos se cambian a mayúsculas
                    parrafo = re.sub(patron, lambda x: x.group().upper(), parrafo)
                interacciones.append(parrafo)

        # Determinar la ruta de salida según si contiene ddi o no y escribir los párrafos
        ruta_salida = path_ddi if contiene_interacciones else path_dii_no
        with open(os.path.join(ruta_salida, file_name_ddi), 'w', encoding="utf-8") as f:
            for parrafo in interacciones:
                f.write("> " + parrafo + '\n')
        return interacciones
