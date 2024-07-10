import os
import re
import pandas as pd
from db_funciones import read_json_file, solicitud_downloadzip_url

# Insertar los datos de PharmGKB: anotaciones clínicas e anotaciones de alélos.

json_file = "properties/properties.json"
data = read_json_file(json_file)
base_path = data["base_path"]
properties = read_json_file(os.path.join(base_path, "properties", "properties.json"))["clinicalannotations"]


def insert_clinial_annotations(session, db):
    """Procesar e insertar los datos de anotaciones clínicas en la bd"""
    # Archivo 1: clinial_annotations.tsv
    columns = properties["clinnan_columns"]
    path = properties["clinann_path"]
    clin_ann = pd.read_table(path, header=0, index_col=False, usecols=columns)
    # Convertir los fármacos en mayúscula y reemplazar caracteres especiales
    clin_ann['Drug(s)'] = clin_ann['Drug(s)'].str.upper()
    clin_ann['Drug(s)'] = clin_ann['Drug(s)'].str.replace(" / ", ", ")
    clin_ann['Drug(s)'] = clin_ann['Drug(s)'].str.replace(";", ", ")
    clin_ann['Gene'] = clin_ann['Gene'].str.replace(";", ", ")

    # En las colummnas variant/haplotypes, genes, cuando hay más de un valor (,), dividir y expandir
    clin_ann["Variant/Haplotypes"] = [re.split(", ", str(var_hap)) for var_hap in clin_ann["Variant/Haplotypes"]]
    clin_ann = clin_ann.explode("Variant/Haplotypes", ignore_index=True)
    # Renombrar las columnas, convertir el df en una lista de diccionarios e insertar en la bd
    clin_ann.columns = ["clinical_annotation_id_var", "variant_haplotypes", "gene_clinann_gkb", "level_of_evidence",
                        "phenotype_category", "drug_clinann_gkb", "phenotypes_clinann_gkb", "url_clinann_gkb"]
    dic_clin_ann = clin_ann.to_dict(orient='records')
    session.bulk_insert_mappings(db, dic_clin_ann)
    session.commit()


def insert_clinical_ann_alleles(session, db):
    """Procesar e insertar los datos de anotaciones de alélos en la bd"""
    # Archivo 2: clinical_ann_alleles.tsv
    columns = properties["clinallele_columns"]
    path = properties["clinallele_path"]
    clin_ann_alleles = pd.read_table(path, header=0, index_col=False, usecols=columns)
    clin_ann_alleles.columns = ["clinical_annotation_id_alleles", "genotype_alleles", "annotation_text_alleles",
                                "allele_function"]
    dic_clin_ann_alleles = clin_ann_alleles.to_dict(orient='records')
    session.bulk_insert_mappings(db, dic_clin_ann_alleles)
    session.commit()


def insert_clinicalann_db(session, db1, db2):
    """Descargar e insertar los datos de anotaciones clínicas en la bd"""
    solicitud_downloadzip_url(properties["download_url"], properties["save_pathZIP"])
    insert_clinial_annotations(session, db1)
    insert_clinical_ann_alleles(session, db2)
