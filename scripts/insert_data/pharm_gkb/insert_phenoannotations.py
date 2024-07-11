import re
import pandas as pd
from db_funciones import read_json_file, solicitud_downloadzip_url

# Insertar los datos de PharmGKB: anotaciones de fenotipos
properties = read_json_file("properties/properties.json")["variantannotations"]


def insert_pheno_annotations(session, db):
    """Procesar e insertar los datos de anotaciones de fenotipos en la bd"""
    # Obtener las columnas, la ruta, leer el archivo y renombrar las columnas
    columns = properties["db_columns_pheno"]
    path = properties["file_path_pheno"]
    pheno_ann = pd.read_table(path, header=0, index_col=False, usecols=columns)
    pheno_ann.columns = ["variant_annotation_id_pheno", "variant_haplotypes_pheno", "gene_pheno", "drugs_pheno",
                         "phenotype_category_pheno", "significance_pheno", "phenotype_annotation_sentence",
                         "metabolizer_types_pheno"]

    # Convertir a mayúsculas y reemplazar caracteres especiales
    pheno_ann['drugs_pheno'] = pheno_ann['drugs_pheno'].str.replace(" / ", ", ")
    pheno_ann['drugs_pheno'] = pheno_ann['drugs_pheno'].str.upper()
    # Dividir y expandir los valores en la columna Variant_Haplotypes
    pheno_ann["variant_haplotypes_pheno"] = [re.split(", ", str(var_hap)) for var_hap in
                                             pheno_ann["variant_haplotypes_pheno"]]
    pheno_ann = pheno_ann.explode("variant_haplotypes_pheno", ignore_index=True)
    # Filtrar las filas por Significance
    pheno_ann = pheno_ann.loc[pheno_ann['significance_pheno'] == "yes"]

    # Función para extraer solo el nombre del gen usando expresiones regulares
    def extract_gene_name(variant):
        # Patrón para capturar nombres de genes y variantes alfanuméricas con caracteres especiales
        gene_name = re.search(r'[A-Z\d\*\-\:]+|[rR][sS]\d+', variant)
        if gene_name:
            return gene_name.group().strip()
        else:
            return None

    # Aplicar la función a la columna 'variant_haplotype' para extraer los nombres de los genes
    pheno_ann['variant_haplotypes_pheno'] = pheno_ann['variant_haplotypes_pheno'].apply(extract_gene_name)
    # Eliminar filas donde la columna 'Drugs' no tiene valores
    pheno_ann = pheno_ann.dropna(subset=['drugs_pheno'])
    # Convertir el df a una lista de diccionarios e insertar los datos en la bd
    pheno_ann_dic = pheno_ann.to_dict(orient='records')
    session.bulk_insert_mappings(db, pheno_ann_dic)
    session.commit()


def insert_phenotannotations_db(session, db):
    """Descagar e insertar los datos a la bd"""
    solicitud_downloadzip_url(properties["download_url"], properties["save_pathZIP"])
    insert_pheno_annotations(session, db)
