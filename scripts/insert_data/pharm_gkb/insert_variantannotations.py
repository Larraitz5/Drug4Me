import re
import pandas as pd
from db_funciones import read_json_file, solicitud_downloadzip_url

# Insertar los datos de PharmGKB: anotaciones de variantes
properties = read_json_file("properties/properties.json")["variantannotations"]


def insert_variantannotations(session, db):
    """Procesar e insertar los datos de anotaciones de variantes en la bd"""
    # Obtener las columnas, la ruta, leer el archivo y renombrar las columnas
    columns = properties["db_columns"]
    path = properties["file_path"]
    variant_ann = pd.read_table(path, header=0, index_col=False, usecols=columns)
    variant_ann.columns = ["variant_annotation_id", "variant_haplotypes", "genes_varann", "drugs_varann",
                           "phenotype_category_varann", "variant_annotation_sentence"]

    # Reemplazar caracteres especiales
    variant_ann['drugs_varann'] = variant_ann['drugs_varann'].str.replace(" / ", ", ")
    variant_ann['drugs_varann'] = variant_ann['drugs_varann'].str.upper()
    # Dividir y expandir en la columna variant_haplotype
    variant_ann["variant_haplotypes"] = [re.split(", ", str(var_hap)) for var_hap in variant_ann["variant_haplotypes"]]
    variant_ann = variant_ann.explode("variant_haplotypes", ignore_index=True)
    # Convertir el df en una lista de diccionarios e insertar los datos en la bd
    variant_ann_dic = variant_ann.to_dict(orient='records')
    session.bulk_insert_mappings(db, variant_ann_dic)
    session.commit()


def insert_variantannotations_db(session, db):
    """Descagar e insertar los datos a la bd"""
    solicitud_downloadzip_url(properties["download_url"], properties["save_pathZIP"])
    insert_variantannotations(session, db)
