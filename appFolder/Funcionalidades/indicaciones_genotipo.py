import re
import pandas as pd
import streamlit as st
from db_connect import session
from db_tables import ClinicalAnnGkb
from app_funciones_funcionalidades import variantes_vcf, get_allele_info

# Funcionalidad 2: Indicaciones PGX basadas en el genotipo


def set_indicaciones_genotipo_page():
    """Definir la página de la funcionalidad 2 de la aplicación"""
    st.subheader(f"**Indicaciones PGx basadas en el genotipo del paciente** :dna:", divider="gray")
    idpaciente = st.text_input("Introduzca el id del paciente:")
    if idpaciente:
        patron = r"^paciente\d+$"
        if re.match(patron, idpaciente):
            # Leer el archivo vcf correspondiente a este paciente y obtener sus variantes
            variantes_paciente = variantes_vcf(idpaciente)
            if type(variantes_paciente) is str:
                st.error(variantes_paciente)
            # Se obtiene la lista de variantes y genotipos del paciente
            else:
                st.write(" ###### **Debe considerar las interacciones entre las variantes y los siguentes "
                         ":red[fármacos], lo que podría causar efectos adversos al paciente.**")
                list_genotipo_paciente = []
                list_mostrar = []
                for variant in variantes_paciente:
                    id_variante = str(variant['ID'])
                    genotype = variant['Genotipo']
                    dicc = {"Variante ID": id_variante, "Genotipo": genotype}
                    list_genotipo_paciente.append(dicc)
                    # Si quiero mostrar la tabla de variantes del paciente, se coge el primer elemento del genotipo
                    dicc_mostrar = {"Variante ID": id_variante, "Genotipo": genotype[0]}
                    list_mostrar.append(dicc_mostrar)
                df_mostrar = pd.DataFrame(list_mostrar)
                st.write("Las variantes de este paciente son:")
                st.write(df_mostrar.T)
                df_genotipo_paciente = pd.DataFrame(list_genotipo_paciente)
                # Se itera sobre cada variante del paciente
                for index, row in df_genotipo_paciente.iterrows():
                    variante_id_paciente = row["Variante ID"]
                    # Buscar si el id de la variante tiene asocaciones fármacos en anotaciones clínicas
                    clinann_variants = session.query(ClinicalAnnGkb).filter(
                        ClinicalAnnGkb.variant_haplotypes == variante_id_paciente).all()
                    # Si interacciona con un solo fármaco
                    if len(clinann_variants) == 1:
                        genotipo_paciente = row["Genotipo"]
                        var_druginterac = []
                        id_clinicalann = clinann_variants[0].clinical_annotation_id_var
                        var_druginterac.append({
                            'Fármaco': clinann_variants[0].drug_clinann_gkb,
                            'Gen': clinann_variants[0].gene_clinann_gkb,
                            'Variante/Haplotipo': clinann_variants[0].variant_haplotypes,
                            'Nivel de Evidencia': clinann_variants[0].level_of_evidence,
                            'Fenotipo': clinann_variants[0].phenotypes_clinann_gkb,
                            'Categoría de Fenotipo': clinann_variants[0].phenotype_category,
                            'URL': clinann_variants[0].url_clinann_gkb,
                            'ID de Anotación Clínica': id_clinicalann})
                        # Se coge el id para buscar las anotaciones de los alelos
                        df_allele_indications, all_genotipes_windications = get_allele_info(id_clinicalann)

                        # Comprobar si el genotipo del paciente está entre los que tienen indicaciones.
                        if len(genotipo_paciente) == 1:  # Es homocigoto:
                            genotipo_paciente = genotipo_paciente[0].upper()
                            if genotipo_paciente in all_genotipes_windications:
                                st.markdown(f"- La variante :red[**{variante_id_paciente}**] con el genotipo "
                                            f"**{genotipo_paciente}**, puede interaccionar con "
                                            f" **{clinann_variants[0].drug_clinann_gkb}**:")
                                df_var_drugintec = pd.DataFrame(var_druginterac)
                                st.data_editor(df_var_drugintec, column_config={"URL": st.column_config.LinkColumn(
                                    "URL", display_text="PharmGKB")})
                                st.markdown(f" &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp"
                                            f";&nbsp; Donde, con el genotipo :red[**{genotipo_paciente}**]:")
                                st.write(df_allele_indications.iloc[:, [1, 2, 3]])
                                st.write("")
                        else:  # Es heterocigoto y genotipo es una lista de len>1
                            genotipo_paciente = [elemento.upper() for elemento in genotipo_paciente]
                            genotipo_paciente_set = set(genotipo_paciente)
                            all_genotipes_windication = set(all_genotipes_windications)
                            # Encontrar la intersección de los conjuntos (se encuentra el genotipo)
                            elementos_comunes = genotipo_paciente_set.intersection(all_genotipes_windication)
                            if elementos_comunes:
                                st.markdown(
                                    f"- La variante :red[**{variante_id_paciente}**] con el genotipo "
                                    f"**{next(iter(elementos_comunes))}**, puede interaccionar con"
                                    f" **{clinann_variants[0].drug_clinann_gkb}**:")
                                df_var_drugintec = pd.DataFrame(var_druginterac)
                                st.data_editor(df_var_drugintec, column_config={"URL": st.column_config.LinkColumn(
                                    "URL", display_text="PharmGKB")})
                                st.markdown(f" &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"
                                            f"&nbsp; Donde, con el genotipo :red[**{next(iter(elementos_comunes))}**]:")
                                st.write(df_allele_indications.iloc[:, [1, 2, 3]])
                                st.write("")

                    # Si la variante genética interacciona con más de un fármaco
                    elif len(clinann_variants) > 1:
                        genotipo_paciente = row["Genotipo"][0]
                        st.markdown(
                            f"- La variante :red[**{variante_id_paciente}**] con el genotipo **{genotipo_paciente}**,"
                            f" puede interaccionar con:")
                        for i, label3 in enumerate(clinann_variants):
                            genotipo_paciente = row["Genotipo"]
                            var_druginterac2 = []
                            st.markdown(f" &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; **{i + 1}) "
                                        f"{label3.drug_clinann_gkb}**")
                            clinical_id = label3.clinical_annotation_id_var
                            var_druginterac2.append({'Fármaco': label3.drug_clinann_gkb, 'Gen': label3.gene_clinann_gkb,
                                                     'Variante/Haplotipo': label3.variant_haplotypes,
                                                     'Nivel de Evidencia': label3.level_of_evidence,
                                                     'Fenotipo': label3.phenotypes_clinann_gkb,
                                                     'Categoría de Fenotipo': label3.phenotype_category,
                                                     'URL': label3.url_clinann_gkb,
                                                     'ID de Anotación Clínica': clinical_id})
                            df_allele_indications, all_genotipes_windications = get_allele_info(clinical_id)
                            if len(genotipo_paciente) == 1:  # Es homocigoto:
                                genotipo_paciente_upper = genotipo_paciente[0].upper()
                                if genotipo_paciente_upper in all_genotipes_windications:
                                    df_var_drugintec = pd.DataFrame(var_druginterac2)
                                    st.data_editor(df_var_drugintec, column_config={"URL": st.column_config.LinkColumn(
                                        "URL", display_text="PharmGKB")})
                                    st.markdown(f"  &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"
                                                f"&nbsp;&nbsp; Donde, con el genotipo "
                                                f":red[**{genotipo_paciente_upper}**]:")
                                    st.write(df_allele_indications.iloc[:, [1, 2, 3]])
                            else:  # Es heterocigoto
                                genotipo_paciente_upper = [elemento.upper() for elemento in genotipo_paciente]
                                genotipo_paciente_set = set(genotipo_paciente_upper)
                                all_genotipes_windication = set(all_genotipes_windications)
                                elementos_comunes = genotipo_paciente_set.intersection(all_genotipes_windication)
                                if elementos_comunes:
                                    df_var_drugintec = pd.DataFrame(var_druginterac2)
                                    st.data_editor(df_var_drugintec, column_config={"URL": st.column_config.LinkColumn(
                                        "URL", display_text="PharmGKB")})
                                    st.markdown(f"  &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"
                                                f"&nbsp;&nbsp; Donde, con el genotipo "
                                                f":red[**{next(iter(elementos_comunes))}**]:")
                                    st.write(df_allele_indications.iloc[:, [1, 2, 3]])
        else:
            st.error("Introduzca un id válido.")
