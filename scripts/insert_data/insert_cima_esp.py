import os
import pandas as pd
from db_funciones import read_json_file, solicitud_downloadfile_url

# Insertar los datos del CIMA

json_file = "properties/properties.json"
data = read_json_file(json_file)
base_path = data["base_path"]
properties = read_json_file(os.path.join(base_path, "properties", "properties.json"))["cima_esp"]


def insert_data_db(session, db):
    """Inserta los datos de CIMA a la base de datos a partir de archivo xls"""
    columns = properties["db_columns"]
    excel_file = properties["file_path"]

    df_cima_med = pd.read_excel(excel_file, usecols=columns)
    df_cima_med = df_cima_med.loc[df_cima_med['Estado'] == "Autorizado"]
    df_cima_med.columns = ["nregistro", "nombre_esp", "laboratorio", "estado", "atc_cima", "principio_activos_cima",
                           "comercializado", "triangulo_amarillo", "observaciones_cima", "afecta_conduccion",
                           "problemas_suministro"]

    # Convertir el DataFrame a una lista de diccionarios
    dic_cima_med = df_cima_med.to_dict(orient='records')
    # Insertar los datos utilizando bulk_save_objects()
    session.bulk_insert_mappings(db, dic_cima_med)
    # Guardar los cambios
    session.commit()


def insert_cima_esp(session, db):
    """Descarga del excel de medicamentos desde el CIMA y procesar e insertar los datos a la bd."""
    solicitud_downloadfile_url(properties["download_url"], properties["file_path"])
    insert_data_db(session, db)
