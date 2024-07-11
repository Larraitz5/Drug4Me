import os
import pandas as pd
from db_funciones import read_json_file, solicitud_downloadzip_url

# Insertar los datos de PharmGKB: asociaciones
properties = read_json_file("properties/properties.json")["relationships"]


def insert_relationships_db(session, db):
    """Procesar e insertar los datos de asociaciones en la bd"""
    # Obtener la ruta y leer el archivo
    path = os.getcwd()
    file_path = properties["save_path"]
    relationships_df = pd.read_table(os.path.join(path, file_path), header=0)

    # Convertir a mayúsculas los nombres de los medicamentos
    relationships_df.loc[relationships_df["Entity1_type"] == "Chemical", "Entity1_name"] = relationships_df.loc[
        relationships_df["Entity1_type"] == "Chemical", "Entity1_name"].str.upper()
    relationships_df.loc[relationships_df["Entity2_type"] == "Chemical", "Entity2_name"] = relationships_df.loc[
        relationships_df["Entity2_type"] == "Chemical", "Entity2_name"].str.upper()

    # Filtrar relaciones donde uno de las entidades es fármaco (Chemical-gen/variant/haplotype)
    filtered_df = relationships_df[
        (((relationships_df["Entity1_type"] == "Chemical") & (relationships_df["Entity2_type"] == "Gene")) | (
                    (relationships_df["Entity1_type"] == "Gene") & (relationships_df["Entity2_type"] == "Chemical")))
        | (((relationships_df["Entity1_type"] == "Chemical") & (relationships_df["Entity2_type"] == "Haplotype")) | (
                    (relationships_df["Entity1_type"] == "Haplotype") & (
                        relationships_df["Entity2_type"] == "Chemical")))
        | (((relationships_df["Entity1_type"] == "Variant") & (relationships_df["Entity2_type"] == "Chemical")) | (
                    (relationships_df["Entity1_type"] == "Chemical") & (
                        relationships_df["Entity2_type"] == "Variant")))]

    # Obtener solo los que están asociados
    relationships_df = filtered_df.loc[filtered_df["Association"] == "associated"]
    # Reemplazar caracteres especiales
    relationships_df.loc[:, 'Entity1_name'] = relationships_df['Entity1_name'].str.replace(" / ", ", ")
    relationships_df.loc[:, 'Entity2_name'] = relationships_df['Entity2_name'].str.replace(" / ", ", ")
    # Renombrar columnas, convertir el df en una lista de diccionarios e insertar los datos en la bd
    relationships_df.columns = ["entity1_id", "entity1_name", "entity1_type", "entity2_id", "entity2_name",
                                "entity2_type", "evidence_relationship", "association_relationships", "pk", "pd",
                                "pmids"]
    relationships_dic = relationships_df.to_dict(orient='records')
    session.bulk_insert_mappings(db, relationships_dic)
    session.commit()


def insert_relationships(session, db):
    """Descagar e insertar los datos a la bd"""
    solicitud_downloadzip_url(properties["download_url"], properties["save_pathZIP"])
    insert_relationships_db(session, db)
