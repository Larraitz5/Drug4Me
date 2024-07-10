import os
import csv
import pandas as pd
from db_funciones import read_json_file, solicitud_downloadfile_url

# Insertar los datos de la base de datos DDinter (drug-drug interactions)

json_file = "properties/properties.json"
data = read_json_file(json_file)
base_path = data["base_path"]
properties = read_json_file(os.path.join(base_path, "properties", "properties.json"))["ddi"]


def read_csv(path):
    """Leer un archivo csv."""
    with open(path) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        df = pd.DataFrame(csv_reader)
    return df


def insertdata_ddi(session, db, path_a, path_b, path_d, path_h, path_l, path_p, path_r, path_v):
    """Procesar los datos del DDinter e insertar a la bd."""
    df_a = read_csv(path_a)
    df_b = read_csv(path_b)
    df_d = read_csv(path_d)
    df_h = read_csv(path_h)
    df_l = read_csv(path_l)
    df_p = read_csv(path_p)
    df_r = read_csv(path_r)
    df_v = read_csv(path_v)
    # Se combinan los 8 dataframes y eliminar duplicados
    combined_df = pd.concat([df_a, df_b, df_d, df_h, df_l, df_p, df_r, df_v])
    unique_df = combined_df.drop_duplicates()
    # Definir la primera fila como encabezado
    new_header = unique_df.iloc[0]
    df_ddi = unique_df[1:]
    df_ddi.columns = new_header
    # Seleccionar las columnas de interés y renombrarlas
    columnas = ["Drug_A", "Drug_B", "Level"]
    df_ddi = df_ddi.loc[:, columnas]
    df_ddi.columns = ["drug_1", "drug_2", "level_ddi"]
    # Convertir los nombres de los fármacos a mayúsculas
    df_ddi['drug_1'] = df_ddi['drug_1'].str.upper()
    df_ddi['drug_2'] = df_ddi['drug_2'].str.upper()
    # Convertir el df a una lista de diccionarios e insertar en la bd
    df_ddi_dic = df_ddi.to_dict(orient='records')
    session.bulk_insert_mappings(db, df_ddi_dic)
    session.commit()


def insert_ddi(session, db):
    """Descargar y procesar los datos del DDinter e insertar a la bd."""
    solicitud_downloadfile_url(properties["download_url_a"], properties["path_a"])
    solicitud_downloadfile_url(properties["download_url_b"], properties["path_b"])
    solicitud_downloadfile_url(properties["download_url_d"], properties["path_d"])
    solicitud_downloadfile_url(properties["download_url_h"], properties["path_h"])
    solicitud_downloadfile_url(properties["download_url_l"], properties["path_l"])
    solicitud_downloadfile_url(properties["download_url_p"], properties["path_p"])
    solicitud_downloadfile_url(properties["download_url_r"], properties["path_r"])
    solicitud_downloadfile_url(properties["download_url_v"], properties["path_v"])
    insertdata_ddi(session, db, properties["path_a"], properties["path_b"], properties["path_d"], properties["path_h"],
                   properties["path_l"], properties["path_p"], properties["path_r"], properties["path_v"])
