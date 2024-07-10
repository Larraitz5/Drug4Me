import os
import re
import pandas as pd
from db_funciones import read_json_file, solicitud_downloadzip_url

# Insertar los datos de PharmGKB: fármacos

json_file = "properties/properties.json"
data = read_json_file(json_file)
base_path = data["base_path"]
properties = read_json_file(os.path.join(base_path, "properties", "properties.json"))["drugs_gkb"]


def insert_drugsgkb_data_db(session, db):
    """Procesar e insertar los datos de fármacos en la bd"""
    # Obtener ruta y leer el archivo
    path = os.getcwd()
    file_path = properties["save_path"]
    columns = properties["db_columns"]
    drugs = pd.read_table(os.path.join(path, file_path), header=0, usecols=columns)

    # Convertir a mayúsculas y reemplazar caracteres especiales
    drugs['Name'] = drugs['Name'].str.replace(" / ", ", ")
    drugs['Generic Names'] = drugs['Generic Names'].str.replace(" / ", ", ")
    drugs['Trade Names'] = drugs['Trade Names'].str.replace(" / ", ", ")
    drugs['Name'] = drugs['Name'].str.upper()
    drugs['Generic Names'] = drugs['Generic Names'].str.upper()
    drugs['Trade Names'] = drugs['Trade Names'].str.upper()
    # Para cada código, dividir y expandir los valores
    columas = ["ATC Identifiers", "RxNorm Identifiers"]
    for column in columas:
        drugs[column] = [re.split(" , ", str(element)) for element in drugs[column]]
        drugs = drugs.explode(column, ignore_index=True)
    # Renombrar columnas, convertir el df a una lista de diccionarios e insertar los datos a la bd
    drugs.columns = ["id_drug", "name_gkb", "generic_name_gkb", "trade_name_gkb", "external_voc_gkb",
                     "rxnorm_identifiers_gkb", "atc_identifiers_gkb"]
    drugs_dic = drugs.to_dict(orient='records')
    session.bulk_insert_mappings(db, drugs_dic)
    session.commit()


def insert_drugs_gkb(session, db):
    """Descagar e insertar los datos a la bd"""
    solicitud_downloadzip_url(properties["download_url"], properties["save_pathZIP"])
    insert_drugsgkb_data_db(session, db)
