import pandas as pd
from unicodedata import normalize
from db_funciones import read_json_file

# Insertar los datos del panel genético
properties = read_json_file("properties/properties.json")["panel_esp"]


def insert_paneldata_db(session, db):
    """Procesar e insertar los datos del panel genético a la bd."""
    # Definir las columnas, leer el archivo y renombrar las columnas
    columns = properties["db_columns"]
    excel_file = properties["file_path"]
    df_panel = pd.read_excel(excel_file, header=0, usecols=columns, skiprows=4)
    df_panel.columns = ["patologia_esp", "gen_esp", "farmaco_esp", "observaciones_esp"]

    # Convertir el nombre de los fármacos a mayúsculas
    farmacos = list(df_panel["farmaco_esp"].str.upper())
    # Eliminar las tildes de los nombres de los fármacos
    df_panel_final_list = []
    trans_tab = dict.fromkeys(map(ord, u'\u0301\u0308'), None)
    for farmaco in farmacos:
        s = normalize('NFKC', normalize('NFKD', farmaco).translate(trans_tab))
        df_panel_final_list.append(s)
    df_panel_final = pd.Series(df_panel_final_list)
    df_panel["farmaco_esp"] = df_panel_final
    # Convertir el df en una lista de diccionarios y añadir a la bd
    dic_panel = df_panel.to_dict(orient='records')
    session.bulk_insert_mappings(db, dic_panel)
    session.commit()
