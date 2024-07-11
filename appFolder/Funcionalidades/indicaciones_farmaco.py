import os
from db_tables import *
from app_funciones_funcionalidades import *
from db_funciones import read_json_file


# Funcionalidad 1: Indicaciones PGX para el fármaco


def set_indicaciones_farmaco_page():
    """Definir la página de la funcionalidad 1 de la aplicación"""
    st.subheader(f"**Indicaciones PGx para el fármaco deseado** :pill: ", divider="gray")
    new_pa = st.text_input("Introduzca el principio activo del nuevo fármaco:")
    new_pa = new_pa.upper()
    # Si introduce el nuevo principio activo
    if new_pa:
        dfopciones_med, dfopciones_medconcom = obtener_mostrar_drugscima(new_pa, "No procede")
        if dfopciones_med is not None and dfopciones_medconcom is not None:
            paselected_esp, atcselected_esp, rxnormid_api = seleccion_drugs(dfopciones_med, dfopciones_medconcom)
            if paselected_esp is not None and atcselected_esp is not None and rxnormid_api is not None:
                # Buscar el nombre en ingles del medicamento seleccionado mediante código ATC, PA y RxNorm.
                # 1. EMA
                atc_ema = session.query(EmaTable).filter(EmaTable.atc_code_ema == atcselected_esp).all()
                paselected_ema = "-"
                # 2. PharmGKB.
                atc_ema, paselected_ema, selected_drug_gkb = find_english_name(paselected_esp, atcselected_esp,
                                                                               rxnormid_api, atc_ema, paselected_ema)
                id_drug_gkb = "-"
                name_drug_gkb = "-"
                rxnorm_drug_gkb = "-"
                if len(selected_drug_gkb) > 0:
                    id_drug_gkb = selected_drug_gkb[0].id_drug
                    name_drug_gkb = selected_drug_gkb[0].name_gkb
                    rxnorm_drug_gkb = selected_drug_gkb[0].rxnorm_identifiers_gkb

                # Mostrar información de los principios activos seleccionados:
                # Si no están disponibles en la EMA ni con la API RxNORM, se cogen de PharmGKB
                if paselected_ema == "-":
                    paselected_ema = name_drug_gkb
                if name_drug_gkb == "-":
                    name_drug_gkb = paselected_ema

                med_en = {paselected_ema, name_drug_gkb}
                if len(med_en) > 1:
                    med_en = f"{paselected_ema} o {name_drug_gkb}"  # Para que busque los dos nombres
                else:
                    med_en = "".join(med_en)
                if rxnormid_api == "-":
                    rxnormid_api = rxnorm_drug_gkb
                df_info = pd.DataFrame({" ": ["RxNorm", "ATC", "Principios Activos", "Principios Activos en Inglés"],
                                        "Medicamento Seleccionado": [rxnormid_api, atcselected_esp, paselected_esp,
                                                                     med_en]})
                st.markdown(f"**TU SELECCIÓN:**")
                st.dataframe(df_info, hide_index=True)

                # Checkbox: seleccionar el nivel de evidencia de las indicaciones
                st.subheader("INDICACIONES FARMACOGENÉTICAS:")
                tab1, tab2 = st.tabs(["**Asociaciones VARIANTE GÉNETICA-FÁRMACO**", "**Asociaciones FÁRMACO-FÁRMACO**"])
                with (tab1):  # VARIANTE GENÉTICA-FÁRMACO
                    tab3_gkb, tab2_ema, tab1_esp = st.tabs(["**PharmGKB**", "**EMA**", "**Panel Genético de España**"])
                    with tab1_esp:  # Panel Genético de España
                        data_panel = get_panelesp_info(paselected_esp)
                        if len(data_panel) > 0:  # Hay indicaciones del panel español
                            panel_df = pd.DataFrame(data_panel)
                            st.text(" EL PANEL GENÉTICO DE ESPAÑA INDICA:")
                            st.write(panel_df.iloc[:, [0, 1, 2]])
                            farmaco = panel_df['Fármaco'].iloc[0]
                            mensajes_impresos = set()
                            # Para no repetir el mensaje
                            for index, row in panel_df.iterrows():
                                farmaco = row["Fármaco"]
                                gen_estudiar = row['Gen o regiones a estudiar']
                                observaciones = row['Observaciones']
                                mensaje = f" Analizar el gen {gen_estudiar} y observar: {observaciones}"
                                if mensaje not in mensajes_impresos:
                                    mensajes_impresos.add(mensaje)
                            st.warning(f"Antes de la prescripción de {farmaco}, se debería proceder a un "
                                       f"test farmacogenómico para:")
                            lista_mensajes = list(mensajes_impresos)
                            for mensaje in lista_mensajes:
                                st.warning(f"- {mensaje}")
                        else:
                            st.error("El panel genético de España no presenta  indicaciones farmacogenéticas para este "
                                     "principio activo")

                    # EMA
                    with tab2_ema:
                        # Si el ATC del medicamento seleccionado está en la EMA
                        if atc_ema:
                            ema_indication = []
                            for objeto in atc_ema:
                                # Obtener la indicacion de cada coincidencia: mediante expresiones regulares,
                                # buscar si trata sobre famarcogenomica (buscando genes, alleles, variant...)
                                indication = objeto.condition_indication_ema
                                regexp = r'CYP|HLA|SLC|\sgenes?\s|\*\d+|allele|mutation|variant|genotype|rs\d+'
                                # Si es de farmacogenetica, se obtienen sus datos
                                if re.search(regexp, indication):
                                    ema_indication.append({'Área terapéutica': objeto.therapeutic_area,
                                                           "Nombre medicamento": objeto.medicine_name_ema,
                                                           "Principios Activos": objeto.active_substance_ema,
                                                           "Código ATC": objeto.atc_code_ema,
                                                           'Indicaciones': objeto.condition_indication_ema,
                                                           'URL': objeto.url_ema})
                            if len(ema_indication) > 0:
                                df_emaindication = pd.DataFrame(ema_indication)
                                st.text("LA EMA INDICA:")
                                st.data_editor(df_emaindication.iloc[:, [0, 1, 2, 3, 5]], column_config={
                                    "URL": st.column_config.LinkColumn("URL", display_text="EMA")})
                                mensaje = df_emaindication.iloc[0, 4]
                                st.warning(mensaje)
                            else:
                                st.error("EMA no presenta  indicaciones farmacogenéticas para este principio activo")
                        else:
                            st.error("EMA no presenta  indicaciones farmacogenéticas para este principio activo")

                    # PharmGKB
                    with tab3_gkb:
                        an_cli, an_clin_det, biomarc, aso_clin = st.tabs(["**Anotaciones Clínicas**",
                                                                          "**Anotaciones en detalle**",
                                                                          "**Biomarcadores**",
                                                                          "**Asociaciones Adicionales**"])
                        # PARTE 1: ANOTACIONES CLÍNICAS (clinical_annotations.tsv + clinical_ann_alleles.tsv)
                        with an_cli:
                            emoji_flechazul = ":arrow_right:"
                            st.subheader(f"**{emoji_flechazul} ANOTACIONES CLÍNICAS**")
                            # Buscar el nombre del fármaco selecciona en clinical annotations.
                            data_clinnan_part1 = []
                            data_clinann_detalles = []  # Para la segunda parte (anotacioens en detalle)
                            clinann_drug = session.query(ClinicalAnnGkb).filter(
                                or_(ClinicalAnnGkb.drug_clinann_gkb == paselected_ema,
                                    ClinicalAnnGkb.drug_clinann_gkb == name_drug_gkb)).all()
                            if len(clinann_drug) > 0:
                                for label in clinann_drug:
                                    data_clinnan_part1.append([label.clinical_annotation_id_var, label.gene_clinann_gkb,
                                                               label.variant_haplotypes, label.level_of_evidence,
                                                               label.url_clinann_gkb])
                                    data_clinann_detalles.append({
                                        'Fármaco': label.drug_clinann_gkb,
                                        'Gen': label.gene_clinann_gkb,
                                        'Variante/Haplotipo': label.variant_haplotypes,
                                        'Nivel de Evidencia': label.level_of_evidence,
                                        'Fenotipo': label.phenotypes_clinann_gkb,
                                        'Categoría de Fenotipo': label.phenotype_category,
                                        'URL': label.url_clinann_gkb,
                                        'ID de Anotación Clínica': label.clinical_annotation_id_var})

                                # En anotaciones clínicas (parte 1): Ordenar la lista según el LOE + mostrar mensajes.
                                data_clinnan_part1 = sorted(data_clinnan_part1, key=lambda x: x[3])
                                if len(data_clinnan_part1) > 0:
                                    st.markdown(
                                        f"##### &nbsp;&nbsp;&nbsp;&nbsp; :red[Es necesario realizar un test "
                                        f"farmacogenómico antes de recetar este medicamento]")
                                    for asociacion in data_clinnan_part1:  # Para que el mensaje salga correctamente
                                        if asociacion[1] is None:  # El gen es None
                                            st.markdown(f"- **Se debe analizar la variante/haplotipo "
                                                        f":red[{asociacion[2]}], con un nivel de evidencia "
                                                        f":red[{asociacion[3]}]. Más información en "
                                                        f"[PharmGKB]({asociacion[4]})**")
                                        if asociacion[2] is None:  # El haplotipo es None
                                            st.markdown(f"- **Se debe analizar el gen :red[{asociacion[1]}], con un"
                                                        f" nivel de evidencia :red[{asociacion[3]}]. Más información "
                                                        f"en [PharmGKB]({asociacion[4]})**")
                                        if asociacion[1] is not None and asociacion[2] is not None:
                                            # Ninguno de los dos es None
                                            st.markdown(f"- **Se debe analizar el gen :red[{asociacion[1]}]  y la "
                                                        f"variante/haplotipo :red[{asociacion[2]}], con un nivel de "
                                                        f"evidencia :red[{asociacion[3]}]. Más información en "
                                                        f"[PharmGKB]({asociacion[4]})**")
                                        # Obtener el id, consultar en clinical_ann_alleles, para obtener la
                                        # anotacion del genotipo/alelo
                                        id_variante = asociacion[0]
                                        ann_alleles = session.query(ClinicalAnnAlleles).filter(
                                            ClinicalAnnAlleles.clinical_annotation_id_alleles == id_variante).all()
                                        an_allele_indications = []
                                        for label in ann_alleles:
                                            an_allele_indications.append({
                                                'ID de Anotación Clínica': label.clinical_annotation_id_alleles,
                                                'Genotipo/Alélo': label.genotype_alleles,
                                                'Texto de Anotación': label.annotation_text_alleles,
                                                'Función del Alélo': label.allele_function, })
                                        df_allele_indications = pd.DataFrame(an_allele_indications)
                                        # Mostrar las anotaciones de alelos para cada anotación clínica en tabla
                                        st.write(df_allele_indications.iloc[:, [1, 2, 3]])
                            else:
                                st.error("No existen asociaciones evidenciadas para éste fármaco.")

                        # PARTE 2: ANOTACIONES CLÍNICAS EN DETALLE
                        with an_clin_det:
                            st.markdown(f" #### **{emoji_flechazul} ANOTACIONES CLÍNICAS EN DETALLE**")
                            # st.markdown(
                            #     "**Asociciones entre el fármaco y variantes genéticas, respaldadas por evidencia "
                            #     "clínica. Estas asociaciones están vinculadas a fenotipos clínicos específicos, "
                            #     "ya sea donde se encontraron estas asociaciones en pacientes con ese "
                            #     "fenotipo/enfermedad, o donde la combinación variante genética-fármaco causa el "
                            #     "fenotipo/enfermedad. Los fenotipos clínicos se clasifican en diferentes categorías "
                            #     "(eficacia, toxicidad, dosificación, metabolismo/PK, PD, otro) indicando posibles "
                            #     "efectos adversos que puede experimentar el paciente o respuestas individuales a "
                            #     "los tratamientos.**")
                            # Anotaciones clinicas para el fármaco seleccionado (obtenido en la parte 1)
                            df_clinann_detalles = pd.DataFrame(data_clinann_detalles)

                            if len(data_clinann_detalles) > 0:
                                # Obtener todos los genes y variantes únicos del df
                                # (para después quitarlos en relationships)
                                unique_genes_clinann = get_unique_genes_variants(df_clinann_detalles['Gen'])
                                unique_variants_clinann = get_unique_genes_variants(
                                    df_clinann_detalles['Variante/Haplotipo'])

                                # Separar el df según el nivel de evidencia: 1,2 y 3,4 (para mostrar)
                                alto_moderado = ["1A", "1B", "2A", "2B"]
                                df_clinann12 = df_clinann_detalles[
                                    df_clinann_detalles['Nivel de Evidencia'].isin(alto_moderado)]
                                df_clinann34 = df_clinann_detalles[
                                    ~df_clinann_detalles['Nivel de Evidencia'].isin(alto_moderado)]
                                # Obtener detalles para imprimir de 1A:
                                # Agrupar por el campo Gen, phen, phen_cat y construir el mensaje para cada grupo
                                df_clinann_1a = df_clinann12[df_clinann12['Nivel de Evidencia'] == "1A"]
                                df_clinann_1a = df_clinann_1a.fillna("-")

                                grouped = df_clinann_1a.groupby(['Gen', 'Fenotipo', 'Categoría de Fenotipo'])
                                anotaciones_altonivel = []
                                for (gen, phen, phen_cat), group in grouped:
                                    groupgen_var = ', '.join(group['Variante/Haplotipo'])
                                    drug = group['Fármaco'].iloc[0]
                                    anotaciones_altonivel.append(
                                        f"###### &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;- Existe una asociación "
                                        f"entre el fármaco :red[{drug}], y los siguentes variantes o "
                                        f"haplotipos: :red[{groupgen_var}] del gen :red[{gen}]. Relacionada con los "
                                        f"siguientes fenotipos: :red[{phen}]. Si se da esta asociación gen-fármaco, "
                                        f"el paciente puede sufrir efectos adversos, como: :red[{phen_cat}].")

                                # Si existen anotaciones, dar opción para mostrar anotaciones de alelos
                                if len(df_clinann12) > 0 or len(df_clinann34) > 0:
                                    st.warning(
                                        """
                                        **Seleccione una fila si quiere obtener más información de cómo la variante 
                                        puede influir en la respuesta al fármaco (fenotipo).**

                                        **Nota:** "None" indica que no hay información correspondiente.""")

                                # Mostrar la tabla y mensajes de niveles 1 y 2:
                                if len(df_clinann12) > 0:
                                    st.markdown("- ##### La siguente tabla muestra las anotaciones clínicas de "
                                                "evidencia :green[alta] o :blue[moderada]:")
                                    selected_row = dataframe_with_selections_url(df_clinann12.iloc
                                                                                 [:, [0, 1, 2, 3, 4, 5, 6, 7]])
                                    # Se permite que solo se seleccione una indicación
                                    if len(selected_row.index) > 1:
                                        st.error("Seleccione una sola anotación")
                                    if len(selected_row.index) == 1:
                                        # Obtener el id, con el cual se hara una consulta a clinical_ann_alleles
                                        id_clin_serie = selected_row['ID de Anotación Clínica']
                                        id_clin_consulta = int(id_clin_serie.iloc[0])
                                        # En este caso no me interasa la segunda variable que devuelve
                                        df_allele_indications, all_genotipes_windications = get_allele_info(
                                            id_clin_consulta)

                                        if len(df_allele_indications) > 0:
                                            st.markdown(f"###### &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"
                                                        f"  - Anotaciones de las variantes genéticas:")
                                            st.write(df_allele_indications.iloc[:, [1, 2, 3]])
                                            st.write("&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; "
                                                     "En los siguientes enlaces puedes obtener más información sobre "
                                                     "la funcionalidad de los alelos: "
                                                     "[PharmGKB](https://www.pharmgkb.org/page/cpicFuncPhen),"
                                                     " [CPIC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC5253119/).")
                                        else:
                                            st.error("No hay anotaciones de alelos para esta anotación clínica.")
                                    if len(df_clinann_1a) > 0 and len(anotaciones_altonivel) < 4:
                                        st.markdown(" ##### &nbsp;&nbsp;&nbsp;&nbsp; **Las anotaciones clínicas con "
                                                    "el nivel de evidencia más :green[ALTO (1A)] indican:**")
                                        for annotation in anotaciones_altonivel:  # Se limita a 4.
                                            st.markdown(annotation)  # Si no, en algunos casos puede ser demasiado.
                                else:
                                    st.write("")

                                # Mostrar la tabla de niveles 3 y 4:
                                if len(df_clinann34) > 0:
                                    st.markdown("")
                                    st.markdown("- ##### La siguente tabla muestra las anotaciones clínicas "
                                                "de evidencia :orange[baja] o :red[nula]:")
                                    selected_row = dataframe_with_selections_url(df_clinann34.iloc
                                                                                 [:, [1, 2, 3, 4, 5, 6, 7]])
                                    # Se permite que solo se seleccione una indicación (este código tengo duplicado)
                                    if len(selected_row.index) > 1:
                                        st.error("Seleccione una sola anotación")
                                    elif len(selected_row.index) == 1:
                                        # obtener el id, con el cual se hara una consulta a clinical_ann_alleles
                                        id_clin_serie = selected_row['ID de Anotación Clínica']
                                        id_clin_consulta = int(id_clin_serie.iloc[0])
                                        # No me interesa la 2ª variable que devuelve (interesa en la funcionalida 3)
                                        df_allele_indications, all_genotipes_windications = get_allele_info(
                                            id_clin_consulta)
                                        if len(df_allele_indications) > 0:
                                            st.markdown(f"###### &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"
                                                        f"  - Anotaciones de las variantes genéticas:")
                                            st.write(df_allele_indications.iloc[:, [1, 2, 3]])
                                            st.write("&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; "
                                                     "En los siguientes enlaces puedes obtener más información sobre "
                                                     "la funcionalidad de los alelos: "
                                                     "[PharmGKB](https://www.pharmgkb.org/page/cpicFuncPhen),"
                                                     " [CPIC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC5253119/).")
                                        else:
                                            st.error("No hay anotaciones de alelos para esta anotación clínica.")
                                else:
                                    st.write("")
                            else:
                                st.error("No existen asociaciones evidenciadas para éste fármaco.")

                            # Añadir información sobre Niveles de Evidencia
                            st.write("")
                            mostrar_loe = st.checkbox("Mostrar información sobre los niveles de evidencia, "
                                                      "según PharmGKB")
                            if mostrar_loe:
                                col1, col2 = st.columns([1, 3.1])
                                with col1:
                                    st.image("data/images/LOE.png", caption="Asignación de niveles de evidencia a las"
                                                                            " anotaciones clínicas",
                                             use_column_width=True)
                                with col2:
                                    st.markdown("""<ul style=" margin-bottom: 0.2em; padding-left: 1.3em;">Existen
                                        anotaciones clínicas de siguientes niveles:<br> <li style="margin-bottom:
                                        0.2em;"><span style="color: green; font-weight: bold;">Nivel 1A:</span>
                                        <span style="font-size: 90%;">Describen combinaciones variante-medicamento
                                        con orientación específica de prescripción en una guía clínica actual o una
                                         etiqueta de medicamento aprobada por la FDA. Deben estar respaldadas por al
                                         menos una publicación adicional además de una guía clínica o etiqueta de
                                         medicamento con orientación específica de prescripción para cada variante.
                                         </li><li style="margin-bottom: 0.2em;"><span style="color: green;
                                         font-weight: bold;">Nivel 1B:</span> <span style="font-size: 90%;">
                                         Describen combinaciones variante-fármaco con un alto nivel de evidencia que
                                          respalda la asociación, pero sin orientación específica para la prescripción
                                          para variantes en una guía clínica o etiqueta de fármaco aprobada por la FDA.
                                          Deben estar respaldadas por al menos dos publicaciones independientes.
                                        </li><li style="margin-bottom: 0.2em;"><span style="color: blue; font-weight:
                                        bold; ">Nivel 2A:</span> <span style="font-size: 90%; ">Describen combinaciones
                                        variante-medicamento encontradas en Genes Farmacogenéticos Muy Importantes
                                        (VIPs) de PharmGKB. Tienen un nivel moderado de evidencia y deben estar
                                        respaldadas por al menos dos publicaciones independientes.</li><li
                                        style="margin-bottom: 0.2em;"><span style="color: blue; font-weight:
                                        bold;">Nivel 2B:</span><span style= "font-size: 90%;"> Describen
                                        combinaciones variante-fármaco con un nivel moderado de evidencia y no se
                                        encuentran en los VIPs de PharmGKB. Deben estar respaldadas por al menos
                                        dos publicaciones independientes.</li><li style="margin-bottom: 0.2em;"><span
                                        style="color: orange; font-weight: bold;">Nivel 3:</span> <span
                                        style="font-size: 90%;">Describen combinaciones variante-medicamento con
                                        un bajo nivel de evidencia.
                                        Pueden basarse en un solo estudio anotado en PharmGKB, o puede haber varios
                                        estudios que no lograron replicar la asociación.</li><li style="margin-bottom:
                                        0.2em;"><span style="color: red; font-weight: bold;">Nivel 4:</span> <span
                                        style="font-size: 90%;">Describen combinaciones variante-fármaco donde la
                                        evidencia no respalda una asociación entre la Variante y el fenotipo del
                                        medicamento, con una puntuación total negativa.</li></ul>""",
                                                unsafe_allow_html=True)

                                url = "https://www.pharmgkb.org/page/clinAnnLevels"
                                st.write("Clique [aquí](%s) para más información sobre los niveles de evidencia." % url)

                        # PARTE 3: BIOMARCADORES, DRUG LABELS (drugLabels.tsv)
                        with biomarc:
                            st.subheader(f"**{emoji_flechazul} BIOMARCADORES FARMACOGENÓMICOS**")
                            st.markdown("**Biomarcadores genéticos y farmacogenómicos asociados al fármaco.**")
                            message = ""
                            # Se consulta si el nombre del pa en inglés está en drugLabels
                            druglabel = session.query(DrugsLabelGkb).filter(or_(
                                DrugsLabelGkb.chemicals_label == paselected_ema,
                                DrugsLabelGkb.chemicals_label == name_drug_gkb)).all()
                            if len(druglabel) > 0:
                                druglabel_data = []
                                for label in druglabel:
                                    # Se obtiene el ID para crear la URL a su anotación
                                    id_url = label.pharmgkb_id_label
                                    url = f"https://www.pharmgkb.org/labelAnnotation/{id_url}"
                                    # Se obtiene su nivel te testeo
                                    if label.testing_level_label == "Testing Required":
                                        message = "test"
                                    elif label.testing_level_label == "Testing Recommended":
                                        message = "recommended"
                                    elif label.testing_level_label == "Actionable PGx":
                                        message = "actionable"
                                    elif label.testing_level_label == "Informative PGx":
                                        message = "informative"
                                    druglabel_data.append(
                                        {"PharmGKB ID": label.pharmgkb_id_label, "Fármaco": label.chemicals_label,
                                         "Genes": label.genes_label, "Variante/Haplotipo":
                                             label.variants_haplotypes_label, "Niveles de testeo":
                                             label.testing_level_label, "Dosis": label.dosing_info_label,
                                         "Fármaco Alternativo": label.alternate_drug_label, "Prescripción":
                                             label.prescribing_label, "Fuente": label.source_label, "URL": url})
                                druglabel_df = pd.DataFrame(druglabel_data)

                                # Mensajes para: tesing level, los genes y variantes, dosing info y prescribing
                                # Obtener todos los GENES únicos del DataFrame en BIOMARCADORES
                                genes_biomarc = druglabel_df['Genes'].dropna().unique()
                                genes_biomarc_ = []
                                for elemento in genes_biomarc:
                                    subelementos = [e.strip() for e in elemento.split(',')]
                                    genes_biomarc_.extend(subelementos)
                                unique_genes_biomarc = list(set(genes_biomarc_))
                                # VARIANTES únicos
                                variants_biomarc = druglabel_df['Variante/Haplotipo'].dropna().unique()
                                variants_biomarc_ = []
                                for elemento in variants_biomarc:
                                    subelementos = [e.strip() for e in elemento.split(',')]
                                    variants_biomarc_.extend(subelementos)
                                unique_variants_biomarc = list(set(variants_biomarc_))

                                #  Crear el mensaje con los GENES Y VARIANTES (si existen)
                                message_genvariant = "-"
                                if unique_genes_biomarc:
                                    message_genvariant = "Es necesario estudiar los siguientes genes: "
                                    message_genvariant += ', '.join(unique_genes_biomarc)
                                if unique_variants_biomarc:
                                    message_genvariant += " y las siguientes variantes: " + ', '.join(
                                        unique_variants_biomarc)

                                # Crear el mensaje para DOSING INFO:
                                message_dosinginfo = "-"
                                if "Dosing Info" in druglabel_df["Dosis"].values:
                                    message_dosinginfo = ("**Debe ajustar la dosis antes de la prescripción de este "
                                                          "medicamento. Consulte la información correspondiente.**")

                                # Crear el mensaje para PRESCRIBING INFO:
                                message_prescribinginfo = "-"
                                if "Prescribing" in druglabel_df["Prescripción"].values:
                                    message_prescribinginfo = (
                                        "**Existe más información para pacientes con un genotipo o fenotipo "
                                        "concreto. Consulte la información correspondiente.**")

                                # Crear y mostrar el mensaje segun el nivel de test
                                if message == "test":
                                    st.markdown(f"##### &nbsp;&nbsp;&nbsp;&nbsp;:red[- Se requiere un test "
                                                f"farmacogenómico antes de prescribir este medicamento.]")
                                elif message == "recommended":
                                    st.markdown(f"##### &nbsp;&nbsp;&nbsp;&nbsp;:orange[- Se recomienda "
                                                f"realizar un test farmacogenómico antes prescribir este "
                                                f"medicamento.]")
                                elif message == "actionable":
                                    st.markdown(f"##### &nbsp;&nbsp;&nbsp;&nbsp;:green[- Revise y considere "
                                                f"las recomendaciones específicas en la etiqueta del fármaco.]")
                                elif message == "informative":
                                    st.markdown(f"##### &nbsp;&nbsp;&nbsp;&nbsp;:blue[Revise y considere las "
                                                f"recomendaciones específicas en la etiqueta del fármaco.]")
                                else:
                                    st.markdown(f"##### &nbsp;&nbsp;&nbsp;&nbsp; - **No se indica el nivel de test.**")

                                # Mostrar mensaje de genes-variantes
                                if message_genvariant != "-":
                                    st.markdown(f"&nbsp;&nbsp;&nbsp;&nbsp; **:red[- {message_genvariant}]**")
                                # De dosing info
                                if message_dosinginfo != "-":
                                    st.markdown(f"&nbsp;&nbsp;&nbsp;&nbsp;- {message_dosinginfo}")
                                # De prescribing info
                                if message_prescribinginfo != "-":
                                    st.markdown(f"&nbsp;&nbsp;&nbsp;&nbsp;- {message_prescribinginfo}")
                                druglabel_df = druglabel_df.iloc[:, [2, 3, 4, 5, 6, 7, 8, 9]]
                                st.data_editor(druglabel_df, column_config={"URL": st.column_config.LinkColumn(
                                    "URL", display_text="PharmGKB")})
                            else:
                                st.error("No hay biomarcadores farmacogenómicos asociados a este medicamento.")

                            # Añadir información de etiquetas de biomarcadores
                            st.write("")
                            info_etiquetas = st.checkbox("Mostrar información sobre las etiquetas, según PharmGKB")
                            if info_etiquetas:
                                st.markdown("""
                                        <ul style="margin-top: 0.2em; margin-bottom: 0.2em; padding-left: 1.5em;">
                                        Niveles de testeo: <br><li style="margin-bottom: 0.2em;"><span style="color:
                                        red;">Testing Required:</span> Indicación de la necesidad de realizar un
                                        análisis genético específico antes de utilizar este medicamento.</li>
                                        <li style="margin-bottom: 0.2em;"><span style="color: orange;">Testing
                                        Recommended:</span> Sugiere que se recomienda realizar un análisis genético
                                        antes de utilizar este medicamento.</li><li style="margin-bottom: 0.2em;">
                                        <span style="color: green;">Actionable PGx:</span> Señala consideraciones
                                        importantes para la prescripción basadas en la genética del paciente al
                                        utilizar este medicamento.</li><li style="margin-bottom: 0.2em;"><span
                                        style="color: blue;">Informative PGx:</span> Proporciona información sobre
                                        variantes genéticas y su impacto en el tratamiento, aunque la mayoría no son
                                        clínicamente significativas.</li></ul>""", unsafe_allow_html=True)

                                st.markdown("""
                                       <ul style="margin-top: 0.2em; margin-bottom: 0.2em; padding-left: 1.5em;">Otras
                                       etiquetas:<li style="margin-bottom: 0.2em;">Dosing Info: Indica que se requiere
                                       ajustar la dosis del medicamento basándose en la genética del paciente.</li>
                                        <li style="margin-bottom: 0.2em;">Alternate Drug: Indica que el fármaco está
                                        contraindicado o no debe ser utilizado, y sugiere considerar otro fármaco basado
                                        en la genética del paciente.</li><li style="margin-bottom: 0.2em;">Prescribing:
                                        Proporciona información adicional para la prescripción de este medicamento en
                                        pacientes con un genotipo particular.</li></ul>""", unsafe_allow_html=True)
                                st.write("Clique [aquí](https://www.pharmgkb.org/page/drugLabelLegend) para "
                                         "más información sobre las etiquetas")

                        # PARTE 4: RELATIONSHIPS (relationships.tsv), VARIANT ANNOTATIONS (var_drug_ann.tsv),
                        # PHENOTYPE ANNOTATIONS (var_pheno_ann.tsv)
                        with aso_clin:
                            st.subheader(f"**{emoji_flechazul} ASOCIACIONES ADICIONALES VARIANTE GENÉTICA-FÁRMACO**")
                            st.markdown("**Además de la información anterior, PharmGKB contempla más asociaciones "
                                        "con diversas fuentes de evidencia, como VIP (Very Important Pharmacogenes), "
                                        "Anotaciones de Variantes, Guía de Dosificación o Rutas Metabólicas.**")
                            st.markdown("**Aunque PharmGKB no ofrece muchos detalles sobre estas relaciones, "
                                        "proporciona estudios (PubMed IDs) que respaldaron dichas asociaciones.**")
                            if id_drug_gkb == "-":
                                st.error("No existe ninguna asociación adicional para este medicamento")
                            else:
                                relationship_iddrug = session.query(RelationshipsGkb).filter(
                                    RelationshipsGkb.entity1_id == id_drug_gkb).all()
                                if len(relationship_iddrug) > 0:
                                    relationships = []
                                    for label in relationship_iddrug:
                                        name1 = label.entity1_name
                                        name2 = label.entity2_name
                                        type2 = label.entity2_type
                                        evidencia = label.evidence_relationship
                                        pmids = label.pmids
                                        # Preparar mensaje de anotaciones de variantes y phenotipo
                                        anotacion_var = "-"
                                        anotacion_pheno = "-"
                                        metabolizer_type = "-"
                                        # Cada relación buscar en var_pheno.tsv
                                        # Usar name 1 y name 2 que serán gen o var/hap con el fármaco
                                        pheno_ann = session.query(PhenoAnnotations).filter(
                                            (PhenoAnnotations.variant_haplotypes_pheno.contains(name1) |
                                             PhenoAnnotations.gene_pheno.contains(name1) |
                                             PhenoAnnotations.drugs_pheno.contains(name1)) &
                                            (PhenoAnnotations.variant_haplotypes_pheno.contains(name2) |
                                             PhenoAnnotations.gene_pheno.contains(name2) |
                                             PhenoAnnotations.drugs_pheno.contains(name2))).all()
                                        if pheno_ann:
                                            # Si existe anotación para esta relacion obtener:
                                            anotacion_pheno = pheno_ann[0].phenotype_annotation_sentence
                                            metabolizer_type = pheno_ann[0].metabolizer_types_pheno
                                            if metabolizer_type is None:
                                                metabolizer_type = "-"

                                        # Cada relación, buscar en var_drug_ann.tsv, si la evidencia = VariantAnnotation
                                        if "VariantAnnotation" in evidencia:
                                            var_ann = session.query(VariantAnnotations).filter(
                                                (VariantAnnotations.variant_haplotypes.contains(name1) |
                                                 VariantAnnotations.genes_varann.contains(name1) |
                                                 VariantAnnotations.drugs_varann.contains(name1)) &
                                                (VariantAnnotations.variant_haplotypes.contains(name2) |
                                                 VariantAnnotations.genes_varann.contains(name2) |
                                                 VariantAnnotations.drugs_varann.contains(name2))).all()
                                            if var_ann:
                                                anotacion_var = var_ann[0].variant_annotation_sentence

                                        # Juntar la información de la relación y las anotaciones de variantes+feno
                                        relationship_info = {'Tipo': type2, 'Nombre': name2, 'Evidencia': evidencia,
                                                             'Anotaciones de variantes': anotacion_var,
                                                             'Anotaciones de fenotipos': anotacion_pheno,
                                                             'Tipo metabolizador': metabolizer_type,
                                                             'PubMed IDs': pmids}
                                        relationships.append(relationship_info)
                                    df_relationships = pd.DataFrame(relationships)
                                    # Eliminar las relaciones que ya están en biomarcadores o clincical annotation y
                                    # que no tienen información en anotaciones
                                    df_relationships['Evidencia'] = df_relationships['Evidencia'].str.split(',')
                                    existe_biomarc = False
                                    try:
                                        condicion_biomarc = (
                                                (df_relationships["Evidencia"].apply(lambda x: "LabelAnnotation" in x))
                                                & (df_relationships["Anotaciones de variantes"] == "-") &
                                                (df_relationships["Anotaciones de fenotipos"] == "-") &
                                                (df_relationships["Tipo metabolizador"] == "-") &
                                                ((df_relationships["Nombre"].isin(unique_genes_biomarc)) | (
                                                    df_relationships["Nombre"].isin(unique_variants_biomarc))))
                                        existe_biomarc = True
                                    except (Exception,):
                                        pass
                                    existe_clinnan = False
                                    try:
                                        condicion_clinnan = (
                                                (df_relationships["Evidencia"].apply(lambda x: "ClinicalAnnotation"
                                                                                               in x)) &
                                                (df_relationships["Anotaciones de variantes"] == "-") &
                                                (df_relationships["Anotaciones de fenotipos"] == "-") &
                                                (df_relationships["Tipo metabolizador"] == "-") &
                                                ((df_relationships["Nombre"].isin(unique_genes_clinann)) | (
                                                    df_relationships["Nombre"].isin(unique_variants_clinann))))
                                        existe_clinnan = True
                                    except (Exception,):
                                        pass
                                    # Se eliminan las filas que cumplen las condiciones
                                    if existe_biomarc is True and existe_clinnan is True:
                                        df_relationships = df_relationships[~(condicion_clinnan | condicion_biomarc)]
                                    elif existe_biomarc is True and existe_clinnan is False:
                                        df_relationships = df_relationships[~condicion_biomarc]
                                    elif existe_biomarc is False and existe_clinnan is True:
                                        df_relationships = df_relationships[~condicion_clinnan]

                                    # Resetear el índice de las filas y cambiar la columna evidencia para mostrar
                                    df_relationships = df_relationships.reset_index(drop=True)
                                    df_relationships['Evidencia'] = df_relationships['Evidencia'].str.join(',')
                                    # Se muestra el df en 3 df para mayor claridad:
                                    if len(df_relationships) > 0:
                                        st.markdown(f"**Fármaco: {name1}**")
                                        # Máscara booleana para filtrar las filas (Sin info en var, phen, tipo_phen)
                                        mask = (df_relationships.iloc[:, [3, 4, 5]] == "-").all(axis=1)
                                        if mask.any():
                                            filtered_df = df_relationships[mask]
                                            st.write(filtered_df.iloc[:, [0, 1, 2, 6]].reset_index(drop=True))
                                        # Las que tienen info en anotaicones de variantes
                                        maskvar = (df_relationships.iloc[:, 3] != "-")
                                        if maskvar.any():
                                            filtered_maskvar = df_relationships[maskvar]
                                            st.markdown(f" **- Anotaciones de Variantes Relacionadas con Fármacos:** se"
                                                        f" muestran anotaciones donde las variantes genéticas afectan "
                                                        f"la respuesta, dosificación, metabolismo u otros aspectos "
                                                        f"relacionados con el fármaco.")
                                            st.write(filtered_maskvar.iloc[:, [0, 1, 2, 3, 6]].reset_index(drop=True))
                                        # Las que tienen info en anotaciones de fenotipo y tipo de metabolizador
                                        maskphen = ~(df_relationships.iloc[:, [4, 5]] == "-").all(axis=1)
                                        if maskphen.any():
                                            filtered_maskphen = df_relationships[maskphen]
                                            st.markdown(f" **- Anotaciones de Variantes que Afectan al Fenotipo:** se "
                                                        f"muestran anotaciones donde las variantes genéticas influyen "
                                                        f"directamente en el fenotipo del paciente.")
                                            st.write(filtered_maskphen.iloc[:, [0, 1, 2, 4, 5, 6]]
                                                     .reset_index(drop=True))
                                        st.write("&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; "
                                                 "En los siguientes enlaces puedes obtener más información sobre "
                                                 "la funcionalidad de los alelos: "
                                                 "[PharmGKB](https://www.pharmgkb.org/page/cpicFuncPhen),"
                                                 " [CPIC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC5253119/).")
                                    else:
                                        st.error("No hay más asociaciones variante genética-fármaco")
                                else:
                                    st.error("No hay más asociaciones variante genética-fármaco")

                with tab2:  # FÁRMACO-FÁRMACO
                    existe_ema = False  # Comprobar que el fármaco seleccionado existe en la EMA
                    hay_prospecto = False  # Comprobar que su prospecto contiene ddi
                    # Obtener el nombre del fármaco (medicine_name de la EMA). Los prospectos están guardados así
                    pa_ema_selected = session.query(EmaTable).filter(EmaTable.active_substance_ema == paselected_ema,
                                                                     EmaTable.atc_code_ema == atcselected_esp).all()
                    # Obtener el medicine name, principios activos y url del fármaco seleccionado.
                    info_drug_selected = []
                    if pa_ema_selected:
                        existe_ema = True
                        medicine_name_selected = pa_ema_selected[0].medicine_name_ema.lower()
                        medicine_name_selected = medicine_name_selected.replace("/", "_").replace(":", "_")
                        pa_prospect_selected = pa_ema_selected[0].active_substance_ema
                        url_prospect_selected = pa_ema_selected[0].url_ema
                        info_drug_selected.append((medicine_name_selected, pa_prospect_selected, url_prospect_selected))

                        # Obtener la ruta a los prospectos
                        ddi_prospecto_nombres = []

                        properties_ema = read_json_file("EMA_DDI/properties_ema/properties_ema.json")["ema"]

                        # Obtener una lista, con tuplas (medicine_name, nombre_archivo)
                        for archivo in (os.listdir(properties_ema["path_ddi"])):
                            partes = archivo.split("_", 1)
                            nombre = partes[1].replace(".txt", "").strip().lower()
                            ddi_prospecto_nombres.append((nombre, archivo))
                        # Comprobar si el medicine_name del fármaco seleccionado está entre los prospectos
                        for (nombre_medicine, nombre_file) in ddi_prospecto_nombres:
                            url_file_prospectdii = info_drug_selected[0][2]
                            if info_drug_selected[0][0] == nombre_medicine:
                                nombre_medicine_prospectddi = nombre_medicine.upper()
                                nombre_file_prospectddi = nombre_file
                                pa_file_prospectddi = info_drug_selected[0][1]
                                hay_prospecto = True

                    ddinter_tab, prospect_tab = st.tabs(
                        ["**DDinter**", "**Prospecto EMA**"])
                    with prospect_tab:
                        if existe_ema:
                            if hay_prospecto:
                                with open(os.path.join(properties_ema["path_ddi"], nombre_file_prospectddi), "r",
                                          encoding="utf-8") as f:
                                    contenido_prospecto = f.readlines()
                                    st.markdown(f"**Nombre del medicamento:** {nombre_medicine_prospectddi}, "
                                                f"**Principio Activo:** {pa_file_prospectddi}")
                                    st.markdown(":arrow_right: **Posibles Interacciones según su prospecto:**")
                                    for linea in contenido_prospecto:
                                        if "-" in linea:
                                            linea = linea.replace("- ", "    -")
                                        if "> " in linea:
                                            linea = linea.replace("> ", "- ")
                                        st.markdown(linea)
                                st.write("")
                                st.write("Para más información sobre este medicamento clique [aquí](%s)." %
                                         url_file_prospectdii)
                            else:
                                st.error("El prospecto no indica ninguna interacción fármaco-fármaco.")
                                st.write("")
                                st.write("Para más información sobre este medicamento clique [aquí](%s)." %
                                         url_file_prospectdii)
                        else:
                            st.error("No se ha encontrado el medicamento en la base de datos de la EMA.")

                    with ddinter_tab:
                        ddi_existe, df_interacciones, ddi_concomi = get_ddi(paselected_esp, paselected_ema,
                                                                            name_drug_gkb, None)
                        if ddi_existe is True:
                            st.write("Se debe considerar que puede haber **interacciones** con los siguientes "
                                     "**fármacos** en caso de tratamiento concomitante.")
                            results1, text2 = st.columns([3.5, 4.5])
                            with results1:
                                if len(ddi_concomi) == 0:
                                    st.write(f"Fármaco: **{paselected_ema}**")
                                    st.write(df_interacciones)
                                else:
                                    for drug in ddi_concomi:
                                        clave, valor = list(drug.items())[0]
                                        st.write(f"Fármaco: **{clave}**")
                                        st.write(valor)
                            with text2:
                                info_gravedad = st.checkbox(
                                    "Mostrar información sobre las categorías de gravedad, según DRUGDEX")
                                if info_gravedad:
                                    st.markdown("""<ul style="margin-top: 0.2em; margin-bottom: 0.2em; padding-left:
                                    1.5em;"<br><li style="margin-bottom: 0.2em;"><span style="color: red;">Major:
                                    </span>Interacciones potencialmente mortales y/o requieren tratamiento médico
                                    o intervención para minimizar o prevenir efectos adversos graves.</li><li
                                    style="margin-bottom: 0.2em;"><span style="color: orange;">Moderate:</span>
                                    Interacciones que pueden resultar en el empeoramiento de la enfermedad del
                                    paciente y/o cambios en la terapia.</li><li style="margin-bottom: 0.2em;"><span
                                     style="color: green;">Minor:</span> Interacciones que pueden limitar los
                                     efectos clínicos. Las manifestaciones pueden incluir un aumento en la
                                     frecuencia o gravedad de los efectos adversos, pero generalmente no requieren
                                     cambios en la terapia.</li><li style="margin-bottom: 0.2em;"><span
                                     style="color: gray;">Unknown:</span> Interacciones que carecen de
                                    descripciones de mecanismos.</li></ul>""", unsafe_allow_html=True)
                                    st.write("")
                                    url = "http://ddinter.scbdd.com/explanation/"  # Error con el wifi de Vicom
                                    st.write("Clique [aquí](%s) para más información." % url)
                        else:
                            st.error("No hay interacciones fármaco-fármaco.")
