import os
import pandas as pd
from db_funciones import read_json_file, solicitud_downloadzip_url

# Insertar los datos de PharmGKB: fármacos biomarcadores

json_file = "properties/properties.json"
data = read_json_file(json_file)
base_path = data["base_path"]
properties = read_json_file(os.path.join(base_path, "properties", "properties.json"))["drugslabel"]


def insert_drugslabel_db(session, db):
    """Procesar e insertar los datos de fármacos biomarcadores en la bd"""
    # Obtener ruta y leer el archivo
    path = os.getcwd()
    file_path = properties["save_path"]
    columns = properties["db_columns"]
    drugslabel = pd.read_table(os.path.join(path, file_path), header=0, usecols=columns)

    # Convertir a mayúsculas y reemplazar caracteres especiales
    drugslabel['Chemicals'] = drugslabel['Chemicals'].str.replace(" / ", ", ")
    drugslabel['Chemicals'] = drugslabel['Chemicals'].str.replace("; ", ", ")
    drugslabel['Genes'] = drugslabel['Genes'].str.replace("; ", ", ")
    drugslabel['Variants/Haplotypes'] = drugslabel['Variants/Haplotypes'].str.replace("; ", ", ")
    drugslabel['Chemicals'] = drugslabel['Chemicals'].str.upper()
    # Filtrar por source: EMA Y FDA
    drugslabel = drugslabel[(drugslabel["Source"] == "FDA") | (drugslabel["Source"] == "EMA")]
    # Renombrar columnas, convertir el df a una lista de diccionarios e insertar los datos a la bd
    drugslabel.columns = ["pharmgkb_id_label", "name_label", "source_label", "biomarker_flag_label",
                          "testing_level_label", "prescribing_info_abel", "dosing_info_label", "alternate_drug_label",
                          "other_prescribing_guidance_label", "cancer_genome", "prescribing_label", "chemicals_label",
                          "genes_label", "variants_haplotypes_label"]

    drugslabel_dic = drugslabel.to_dict(orient='records')
    session.bulk_insert_mappings(db, drugslabel_dic)
    session.commit()


def insert_drugslabels(session, db):
    """Descagar e insertar los datos a la bd"""
    solicitud_downloadzip_url(properties["download_url"], properties["save_pathZIP"])
    insert_drugslabel_db(session, db)
