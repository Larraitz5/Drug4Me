import os
import re
import pandas as pd
from db_funciones import read_json_file, solicitud_downloadfile_url

# Insertar los datos de la EMA

json_file = "properties/properties.json"
data = read_json_file(json_file)
base_path = data["base_path"]
properties = read_json_file(os.path.join(base_path, "properties", "properties.json"))["ema"]


def insert_emadata_db(session, db):
    """Procesar e insertar los datos de la EMA a la bd."""
    # Definir las columnas y leer el archivo
    columns = properties["db_columns"]
    excel_file = properties["file_path"]
    df_ema = pd.read_excel(excel_file, header=0, skiprows=8, usecols=columns)
    # Convertir a mayúscula los principios activos y filtrar por humanos y autorizados
    df_ema['Active substance'] = df_ema['Active substance'].str.upper()
    df_ema = df_ema.loc[df_ema['Category'] == "Human"]
    df_ema = df_ema.loc[df_ema['Authorisation status'] == "Authorised"]
    # Renombrar columnas
    df_ema.columns = ["category_ema", "medicine_name_ema", "therapeutic_area", "inn_common_name_ema",
                      "active_substance_ema", "authorisation_status_ema", "atc_code_ema", "condition_indication_ema",
                      "url_ema"]
    # Dividir (por comas) y expandir los códigos ATC
    df_ema["atc_code_ema"] = [re.split(", ", str(code)) for code in df_ema["atc_code_ema"]]
    df_ema = df_ema.explode("atc_code_ema", ignore_index=True)

    dic_ema = df_ema.to_dict(orient='records')
    session.bulk_insert_mappings(db, dic_ema)
    session.commit()


def insert_ema(session, db):
    """Descargar y procesar los datos de la EMA e insertar a la bd."""
    solicitud_downloadfile_url(properties["download_url"], properties["file_path"])
    insert_emadata_db(session, db)
