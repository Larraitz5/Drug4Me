from app_funciones_funcionalidades import *
from db_tables import ClinicalAnnGkb, EmaTable

# Funcionalidad 3: Medicina de Presición


def set_medicina_precision_page():
    """Definir la página de la funcionalidad 3 de la aplicación"""
    st.subheader(f" **Medicina de Precisión** :female-doctor: :male-doctor: ", divider="gray")
    paciente_col, farmaco_col = st.columns([4.5, 4.5])
    with paciente_col:
        idpaciente_mp = st.text_input(":pushpin: Introduzca el id del paciente:")
        if idpaciente_mp:
            patron = r"^paciente\d+$"
            if re.match(patron, idpaciente_mp):
                variantes_paciente = variantes_vcf(idpaciente_mp)
                if type(variantes_paciente) is str:
                    st.error(variantes_paciente)
                else:
                    st.markdown("Paciente identificado :heavy_check_mark:")
                    list_var_genotipo_paciente = []
                    for variant in variantes_paciente:
                        list_var_genotipo_paciente.append({str(variant['ID']): (variant['Genotipo'])})

                    # Para cada variante_id del paciente, se buscan los fármacos con los que interacciona
                    dicc_var_drug_paciente = {}  # {id_variante: farmacos_interacciona}
                    for dicc in list_var_genotipo_paciente:
                        variante_id_paciente, valor = list(dicc.items())[0]
                        clinann_variants = session.query(ClinicalAnnGkb).filter(
                            ClinicalAnnGkb.variant_haplotypes == variante_id_paciente).all()
                        for interaccion in clinann_variants:
                            if variante_id_paciente in dicc_var_drug_paciente:
                                dicc_var_drug_paciente[variante_id_paciente].append([interaccion.drug_clinann_gkb])
                            else:
                                dicc_var_drug_paciente[variante_id_paciente] = [[interaccion.drug_clinann_gkb]]
            else:
                st.error("Introduzca un id válido.")

    with farmaco_col:
        new_pa = st.text_input(":pushpin: Introduzca el principio activo del fármaco a recetar:")
        new_pa = new_pa.upper()

    # Multiselect para añadir los medicamentos que se está tomando
    opciones_pa_cima = []
    opciones_cima = session.query(Drugscima).all()
    for drug in opciones_cima:
        opciones_pa_cima.append(drug.principio_activos_cima)
    opciones_pa_cima = list(set(opciones_pa_cima))
    drugs_paciente_multiselect = st.multiselect(" :pushpin:  Introduce los medicamentos que se está tomando el "
                                                "paciente si es el caso:", opciones_pa_cima, placeholder="")
    st.markdown("")

    if new_pa:
        dfopciones_med, dfopciones_medmas = obtener_mostrar_drugscima(new_pa, idpaciente_mp)
        if dfopciones_med is not None and dfopciones_medmas is not None and idpaciente_mp:
            pa_selected, atc_selected, rxnormid_api = seleccion_drugs(dfopciones_med, dfopciones_medmas)
            if pa_selected is not None and atc_selected is not None and rxnormid_api is not None:
                # Buscar el nombre en ingles del medicamento seleccionado mediante código ATC, PA y RxNorm.
                # 1. EMA
                atc_ema = session.query(EmaTable).filter(EmaTable.atc_code_ema == atc_selected).all()
                paselected_ema = "-"
                # 2. PharmGKB
                atc_ema, paselected_ema, selected_drug_gkb = find_english_name(pa_selected, atc_selected, rxnormid_api,
                                                                               atc_ema, paselected_ema)
                name_drug_gkb = "-"
                if len(selected_drug_gkb) > 0:
                    name_drug_gkb = selected_drug_gkb[0].name_gkb

                # Si no está disponible ni en la EMA ni con la API RxNorm, se cogen de PharmGKB
                if paselected_ema == "-" and name_drug_gkb == "-":
                    med_en = "-"
                if paselected_ema == "-":
                    paselected_ema = name_drug_gkb
                if name_drug_gkb == "-":
                    name_drug_gkb = paselected_ema

                # Para mostrar correctamente
                med_en = {paselected_ema, name_drug_gkb}
                if len(med_en) > 1:
                    med_en = f"{paselected_ema} o {name_drug_gkb}"  # Para que busque los dos nombres
                else:
                    med_en = "".join(med_en)

                if paselected_ema == "-" and name_drug_gkb == "-":
                    st.warning(f"No se ha encontrado este fármaco en la base de datos.")
                else:
                    df_seleccion = pd.DataFrame([[med_en, atc_selected]], columns=["FÁRMACO",
                                                                                           "CÓDIGO ATC"])
                    st.markdown(f"**TU SELECCIÓN:**")
                    st.write(df_seleccion)

                    var_int, drug_int = st.tabs(["**Asociaciones VARIANTE GENÉTICA-FÁRMACO**",
                                                 "**Asociaciones FÁRMACO-FÁRMACO**"])
                    with var_int:
                        var_far_int = False
                        pa_all_selected = []  # Para medicamentos concomitantes (tendrá todos los pa alfabeticamente)

                        # Obtener en una lista todos los fármacos que interaccionan con la variante
                        for var_paciente, drugs_paciente in dicc_var_drug_paciente.items():
                            all_drugs_paciente = []
                            for drug in drugs_paciente:
                                all_drugs_paciente.append(drug[0])
                                if ", " in drug[0]:
                                    drugs_split = drug[0].split(", ")
                                    for elemento in drugs_split:
                                        all_drugs_paciente.append(elemento)

                            # Buscar el genotipo del paciente con el id de la variante
                            for dicc in list_var_genotipo_paciente:
                                if var_paciente in dicc:
                                    genotipo_paciente = dicc[var_paciente]

                            # Generar una lista ordenada con todos los pa en caso de tratamiento concomitante
                            if "," in name_drug_gkb:
                                # Se obtienen los PA individuales y en conjunto para luego poder obtener ddi
                                name_drug_gkb_split = name_drug_gkb.split(", ")
                                for pa in name_drug_gkb_split:
                                    if pa not in pa_all_selected:
                                        pa_all_selected.append(pa)
                                paema_list = [pa_.strip() for pa_ in name_drug_gkb.split(',')]
                                paema_list.sort()
                                pname_drug_gkb_sorted = ', '.join(paema_list)
                                pa_all_selected.append(pname_drug_gkb_sorted)
                                pa_all_selected = list(set(pa_all_selected))

                            if "," not in name_drug_gkb:
                                # Si el fármaco seleccionado está entre los fármacos que interacciona la variable
                                if name_drug_gkb in all_drugs_paciente:
                                    clinann_variants = session.query(ClinicalAnnGkb).filter(
                                        ClinicalAnnGkb.variant_haplotypes == var_paciente,
                                        or_(ClinicalAnnGkb.drug_clinann_gkb == name_drug_gkb,
                                            ClinicalAnnGkb.drug_clinann_gkb.contains(name_drug_gkb))).all()
                                    if len(clinann_variants) == 1:
                                        var_far_int = True
                                        coinci_var_drug = [{
                                            'Fármaco': clinann_variants[0].drug_clinann_gkb,
                                            'Gen': clinann_variants[0].gene_clinann_gkb,
                                            'Variante/Haplotipo': clinann_variants[0].variant_haplotypes,
                                            'Nivel de Evidencia': clinann_variants[0].level_of_evidence,
                                            'Fenotipo': clinann_variants[0].phenotypes_clinann_gkb,
                                            'Categoría de Fenotipo': clinann_variants[0].phenotype_category,
                                            'URL': clinann_variants[0].url_clinann_gkb,
                                            'ID de Anotación Clínica':
                                                clinann_variants[0].clinical_annotation_id_var}]
                                        df_coinci_var_drug = pd.DataFrame(coinci_var_drug)
                                        # Se buscan las anotaciones de alelos
                                        df_allele_indications, all_genotipes_windications = get_allele_info(
                                            clinann_variants[0].clinical_annotation_id_var)
                                        if len(genotipo_paciente) == 1:  # Es homocigoto
                                            genotipo_paciente_upper = genotipo_paciente[0].upper()
                                            if genotipo_paciente_upper in all_genotipes_windications:
                                                st.markdown(f"- El paciente tiene la variante "
                                                            f":red[**{var_paciente}**] con el genotipo "
                                                            f"**{genotipo_paciente_upper}** que puede interaccionar"
                                                            f" con **{name_drug_gkb}**:")
                                                st.data_editor(df_coinci_var_drug,
                                                               column_config={"URL": st.column_config.LinkColumn(
                                                                   "URL", display_text="PharmGKB")})
                                                st.markdown(
                                                    f" &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp"
                                                    f";&nbsp;&nbsp;&nbsp; Donde, con el genotipo "
                                                    f":red[**{genotipo_paciente_upper}**]:")
                                                st.write(df_allele_indications.iloc[:, [1, 2, 3]])
                                        else:  # Es heterocigoto
                                            genotipo_paciente_upper = [elemento.upper() for elemento
                                                                       in genotipo_paciente]
                                            genotipo_paciente_set = set(genotipo_paciente_upper)
                                            all_genotipes_windication = set(all_genotipes_windications)
                                            # Encontrar la intersección de los conjuntos (se encuentra el genotipo)
                                            elementos_comunes = genotipo_paciente_set.intersection(
                                                all_genotipes_windication)
                                            if elementos_comunes:
                                                st.markdown(
                                                    f"- El paciente tiene la variante :red[**{var_paciente}**] con"
                                                    f" el genotipo **{next(iter(elementos_comunes))}** que puede "
                                                    f"interaccionar con **{name_drug_gkb}**:")
                                                st.data_editor(df_coinci_var_drug,
                                                               column_config={"URL": st.column_config.LinkColumn(
                                                                   "URL", display_text="PharmGKB")})
                                                st.markdown(
                                                    f" &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp"
                                                    f";&nbsp;&nbsp;&nbsp; Donde, con el genotipo "
                                                    f":red[**{next(iter(elementos_comunes))}**]:")
                                                st.write(df_allele_indications.iloc[:, [1, 2, 3]])

                                    elif len(clinann_variants) > 1:
                                        var_far_int = True
                                        st.markdown(
                                            f"- El paciente tiene la variante :red[**{var_paciente}**] con el "
                                            f"genotipo **{genotipo_paciente[0]}**,"
                                            f" puede interaccionar con:")
                                        for i, element in enumerate(clinann_variants):
                                            coinci_var_drug = [{
                                                'Fármaco': element.drug_clinann_gkb,
                                                'Gen': element.gene_clinann_gkb,
                                                'Variante/Haplotipo': element.variant_haplotypes,
                                                'Nivel de Evidencia': element.level_of_evidence,
                                                'Fenotipo': element.phenotypes_clinann_gkb,
                                                'Categoría de Fenotipo': element.phenotype_category,
                                                'URL': element.url_clinann_gkb,
                                                'ID de Anotación Clínica': element.clinical_annotation_id_var}]
                                            st.markdown(
                                                f" &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; **{i + 1}) "
                                                f"{element.drug_clinann_gkb}**")
                                            df_coinci_var_drug = pd.DataFrame(coinci_var_drug)

                                            df_allele_indications, all_genotipes_windications = get_allele_info(
                                                element.clinical_annotation_id_var)
                                            if len(genotipo_paciente) == 1:  # Es homocigoto
                                                genotipo_paciente_upper = genotipo_paciente[0].upper()
                                                if genotipo_paciente_upper in all_genotipes_windications:
                                                    st.data_editor(df_coinci_var_drug,
                                                                   column_config={"URL": st.column_config.LinkColumn(
                                                                       "URL", display_text="PharmGKB")})
                                                    st.markdown(
                                                        f"  &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"
                                                        f"&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; Donde, con el "
                                                        f"genotipo :red[**{genotipo_paciente_upper}**]:")
                                                    st.write(df_allele_indications.iloc[:, [1, 2, 3]])
                                            else:  # Es heterocigoto
                                                genotipo_paciente_upper = [elemento.upper() for elemento in
                                                                           genotipo_paciente]
                                                genotipo_paciente_set = set(genotipo_paciente_upper)
                                                all_genotipes_windication = set(all_genotipes_windications)
                                                elementos_comunes = genotipo_paciente_set.intersection(
                                                    all_genotipes_windication)
                                                if elementos_comunes:
                                                    st.data_editor(df_coinci_var_drug,
                                                                   column_config={"URL": st.column_config.LinkColumn(
                                                                       "URL", display_text="PharmGKB")})
                                                    st.markdown(
                                                        f"  &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp"
                                                        f";&nbsp;&nbsp;&nbsp;&nbsp; Donde, con el genotipo "
                                                        f":red[**{next(iter(elementos_comunes))}**]:")
                                                    st.write(df_allele_indications.iloc[:, [1, 2, 3]])

                            else:  # Selección de un fármaco concomitante
                                contador = 0
                                interac = []  # Fármacos en común entre los pa seleccionados y del paciente
                                for drug_selected in pa_all_selected:
                                    for drug_paciente in all_drugs_paciente:
                                        if drug_selected in drug_paciente or drug_selected == drug_paciente:
                                            if drug_paciente not in interac:
                                                interac.append(drug_paciente)

                                if len(interac) >= 1:  # Se enumera cada fármaco
                                    st.markdown(
                                        f"- El paciente tiene la variante :red[**{var_paciente}**] con el "
                                        f"genotipo **{genotipo_paciente[0].upper()}** que puede interaccionar "
                                        f"con:")
                                    var_far_int = True
                                    for drug in interac:
                                        all_clinan = []
                                        clinann_variants = session.query(ClinicalAnnGkb).filter(
                                            ClinicalAnnGkb.variant_haplotypes == var_paciente,
                                            ClinicalAnnGkb.drug_clinann_gkb == drug).all()
                                        if len(clinann_variants) == 1:
                                            contador += 1
                                            all_clinan.append({contador: clinann_variants})
                                        else:
                                            for clin in clinann_variants:
                                                contador += 1
                                                all_clinan.append({contador: [clin]})

                                        for dicc in all_clinan:
                                            for key, value in dicc.items():
                                                element = value[0]
                                                st.markdown(f" &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; "
                                                            f"**{key}) {drug}**")
                                                coinci_var_drug = [{
                                                    'Fármaco': element.drug_clinann_gkb,
                                                    'Gen': element.gene_clinann_gkb,
                                                    'Variante/Haplotipo': element.variant_haplotypes,
                                                    'Nivel de Evidencia': element.level_of_evidence,
                                                    'Fenotipo': element.phenotypes_clinann_gkb,
                                                    'Categoría de Fenotipo': element.phenotype_category,
                                                    'URL': element.url_clinann_gkb,
                                                    'ID de Anotación Clínica': element.clinical_annotation_id_var}]
                                                df_coinci_var_drug = pd.DataFrame(coinci_var_drug)
                                                st.data_editor(df_coinci_var_drug,
                                                               column_config={"URL": st.column_config.LinkColumn(
                                                                   "URL", display_text="PharmGKB")})

                                                df_allele_indications, all_genotipes_windications = get_allele_info(
                                                    element.clinical_annotation_id_var)
                                                if len(genotipo_paciente) == 1:  # Es homocigoto
                                                    genotipo_paciente_upper = genotipo_paciente[0].upper()
                                                    if genotipo_paciente_upper in all_genotipes_windications:
                                                        st.markdown(f" &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp"
                                                                    f";&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; Donde, "
                                                                    f"con el genotipo "
                                                                    f":red[**{genotipo_paciente_upper}**]:")
                                                        st.write(df_allele_indications.iloc[:, [1, 2, 3]])
                                                else:  # Es heterocigoto
                                                    genotipo_paciente_upper = [elemento.upper() for elemento
                                                                               in genotipo_paciente]
                                                    genotipo_paciente_set = set(genotipo_paciente_upper)
                                                    all_genotipes_windication = set(all_genotipes_windications)
                                                    elementos_comunes = genotipo_paciente_set.intersection(
                                                        all_genotipes_windication)
                                                    if elementos_comunes:
                                                        st.markdown(
                                                            f" &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"
                                                            f"&nbsp;&nbsp;&nbsp;&nbsp; Donde, con el genotipo "
                                                            f":red[**{next(iter(elementos_comunes))}**]:")
                                                        st.write(df_allele_indications.iloc[:, [1, 2, 3]])
                        if var_far_int is not True:
                            st.error(
                                f"No existen indicaciones de interacciones entre las variantes genéticas de este "
                                f"paciente y {name_drug_gkb}.")

                    with drug_int:
                        mensaje_tomando_seleccionado = False
                        ddi_existe, df_interacciones, ddi_concomi = get_ddi(pa_selected, paselected_ema, name_drug_gkb,
                                                                             pa_all_selected)
                        if ddi_existe is True:
                            drugs_tomando = []
                            if drugs_paciente_multiselect:
                                #  Para cada fármaco que se toma el paciente, buscar su correspondencia en inglés.
                                for drug_tomando in drugs_paciente_multiselect:
                                    atc_cima_tomando = session.query(Drugscima).filter(
                                        Drugscima.principio_activos_cima == drug_tomando).all()
                                    # Se coge la primera coincidencia y su atc
                                    atc_cima_tomando = atc_cima_tomando[0].atc_cima
                                    atc_ema_tomando = session.query(EmaTable).filter(
                                        EmaTable.atc_code_ema == atc_cima_tomando).all()
                                    paselected_ema_tomando = "-"
                                    rxnormid_api_tomando = get_rxcui(atc_cima_tomando)
                                    # Buscar el drug seleccionado EN PharmGKB.
                                    atc_ema_tom_eng, paselected_ema_tom_eng, selected_drug_gkb_tom_eng = find_english_name(
                                        drug_tomando, atc_cima_tomando, rxnormid_api_tomando, atc_ema_tomando,
                                        paselected_ema_tomando)
                                    name_drug_gkb_tom_eng = "-"
                                    if len(selected_drug_gkb_tom_eng) > 0:
                                        name_drug_gkb_tom_eng = selected_drug_gkb_tom_eng[0].name_gkb
                                    if paselected_ema_tom_eng == "-":
                                        paselected_ema_tom_eng = name_drug_gkb_tom_eng
                                    drugs_tomando.append((name_drug_gkb_tom_eng, paselected_ema_tom_eng))

                            if len(ddi_concomi) == 0:
                                # Verificar si el fármaco seleccionado interacciona con fármacos que se esta tomando
                                for (name_drug_gkb_tom_eng, paselected_ema_tom_eng) in drugs_tomando:
                                    for indice, drug_int in df_interacciones.iterrows():
                                        if name_drug_gkb_tom_eng == drug_int.Interacciones or paselected_ema_tom_eng == drug_int.Interacciones:
                                            if not mensaje_tomando_seleccionado:
                                                st.markdown("**Posibles :red[interacciones] entre el fármaco que se "
                                                            "está tomando este paciente y el que se va a recetar:**")
                                                mensaje_tomando_seleccionado = True
                                            # Encontrar el color de la gravedad
                                            if drug_int.Gravedad == "Major":
                                                color = "red"
                                            elif drug_int.Gravedad == "Moderate":
                                                color = "orange"
                                            elif drug_int.Gravedad == "Minor":
                                                color = "green"
                                            else:
                                                color = "gray"
                                            st.markdown(f"- **:red[{drug_int.Interacciones}] - :red[{name_drug_gkb}], "
                                                        f"con un nivel de gravedad: :{color}[{drug_int.Gravedad}].**")
                                if len(df_interacciones) > 0:
                                    st.write("Se debe considerar que puede haber **interacciones** con los siguientes "
                                             "**fármacos** en caso de tratamiento concomitante:")
                                    st.write(f"Fármaco: **{name_drug_gkb}**")
                                    st.write(df_interacciones)
                            else:
                                for drug in ddi_concomi:
                                    clave, valor = list(drug.items())[0]
                                    for i, row in valor.iterrows():
                                        drug_interacciones = row.Interacciones
                                        for (name_drug_gkb_tom_eng, paselected_ema_tom_eng) in drugs_tomando:
                                            if name_drug_gkb_tom_eng == drug_interacciones or paselected_ema_tom_eng == drug_interacciones:
                                                if not mensaje_tomando_seleccionado:
                                                    st.markdown(
                                                            "**Posibles :red[interacciones] entre el fármaco que se "
                                                            "está tomando este paciente y el que se va a recetar:**")
                                                    mensaje_tomando_seleccionado = True
                                                st.markdown(f"- **:red[{drug_interacciones}] - :red[{clave}], con un "
                                                            f"nivel de gravedad: {row.Gravedad}.**")
                                if len(ddi_concomi) > 0:
                                    st.write(
                                        "Se debe considerar que puede haber **interacciones** con los siguientes "
                                        "**fármacos** en caso de tratamiento concomitante:")
                                cols = st.columns(len(ddi_concomi))
                                for col, drug in zip(cols, ddi_concomi):
                                    clave, valor = list(drug.items())[0]
                                    with col:
                                        st.write(f"Fármaco: **{clave}**")
                                        st.write(valor)
                        else:
                            st.error("No hay interacciones fármaco-fármaco.")
