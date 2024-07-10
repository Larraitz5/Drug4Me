import re
import requests
import pandas as pd
import streamlit as st
from sqlalchemy import or_
from db_connect import session
from db_tables import Drugscima, DrugsGkb, PanelGeneticoEsp, ClinicalAnnAlleles, DrugDrugInteractions

# Funciones para las funcionalidades


def obtener_mostrar_drugscima(new_pa, idpaciente_mp):
    """Obtiene desde el CIMA los fármacos que contienen el princpio activo introducido y
    crea dos dataframes para mostrar todas las opciones : uno con los fármacos con ese principio activo y
    otro con los fármacos concomitantes.
    Recibe: el principio activo, y el id del paciente (solo en la funcionalidad 3).
    Devuelve los dos dataframes si existen fármacos con el principio activo y/o si existe el id del paciente.
    Devuelve None si no existen fármacos o si falta introducir correctamente el id del paciente. """
    pattern = r"\b" + re.escape(new_pa) + r"\b"  # Coincidencias exactas
    farmacos_cima_ = session.query(Drugscima).filter(Drugscima.principio_activos_cima.op('regexp')(pattern)).all()
    if len(farmacos_cima_) == 0:  # Si no está en la bd del CIMA
        st.error("Este prinpio activo no existe en la base de datos del CIMA")
        return None, None
    else:  # Si está en el CIMA, se obtienen farmacos con solo ese pa y los concomitantes
        opciones_med = set()
        opciones_concom = set()
        for farmaco in farmacos_cima_:
            pa = farmaco.principio_activos_cima.strip()
            atc = farmaco.atc_cima.strip()
            if "," in pa:  # Fármaco concomitante
                opciones_concom.add((pa, atc))
            else:
                opciones_med.add((pa, atc))
        # Obtener un df con los fármacos con un pa, y otro con fármacos concomitantes
        columns = ["Principios Activos", "Código ATC"]
        dfopciones_med = pd.DataFrame(opciones_med, columns=columns)
        dfopciones_medconcom = pd.DataFrame(opciones_concom, columns=columns)
        if idpaciente_mp == "No procede":
            st.markdown("Entre los **Medicamentos autorizados en España** , seleccione el medicamento que desea "
                        "recetar:")
            return dfopciones_med, dfopciones_medconcom
        elif idpaciente_mp:
            st.markdown("Entre los **Medicamentos autorizados en España** , seleccione el medicamento que desea "
                        "recetar:")
            return dfopciones_med, dfopciones_medconcom
        else:
            st.warning("Intoduce el id del paciente para proceder")
            return None, None


def get_rxcui(atc):
    """Obtener el código rxcui del RxNorm a partir del ATC de un medicamento.
    Recibe el código ATC.
    Devuelve el código rxcui del medicamento (puede ser None or "NaN")."""
    # Parámetros y variables
    params = {'idtype': 'ATC', 'id': atc}
    response = requests.get('https://rxnav.nlm.nih.gov/REST/rxcui.json', params=params)
    response_dict = response.json()
    try:
        rxcui = response_dict['idGroup']['rxnormId'][0]
    except (IndexError, KeyError):
        rxcui = "NaN"
    return rxcui


def dataframe_with_selections(df):
    """Permite selecionar filas en un df.
    Recibe un df.
    Devuelve un df con las filas seleccionadas"""
    df_with_selections = df.copy()
    df_with_selections.insert(0, "Seleccionar", False)  # Insertar la 1ª columna Select
    edited_df = st.data_editor(df_with_selections, hide_index=True,
                               column_config={"Seleccionar": st.column_config.CheckboxColumn(required=True)},
                               disabled=df.columns, )
    selected_rows = edited_df[edited_df.Seleccionar]  # Obtener la fila seleccionada
    return selected_rows.drop('Seleccionar', axis=1)  # Devuleve el df(fila) seleccionado sin la columna select


def seleccion_drugs(dfopciones_med, dfopciones_medmas):
    """Genera y muestra df con la opción de selección para un solo fármaco.
    Se obtienen el principio activo, atc y rxnorm del fármaco seleccionado.
    Recibe dos dataframes.
    Devuelve, si se elige un fármaco, su principio activo, atc y rxnorm. Si no, devuelve None."""
    col1, col2 = st.columns([3.5, 4.5])
    selec_userleft = pd.DataFrame()
    selec_useright = pd.DataFrame()
    # Mostrarlos con la opción de seleccionar un solo fármaco
    with col1:
        if len(dfopciones_med) > 0:
            st.markdown("- Fármacos con el principio activo introducido:")
            selec_userleft = dataframe_with_selections(dfopciones_med)
        else:
            st.write("")
    with col2:
        if len(dfopciones_medmas) > 0:
            st.markdown("- Tratamientos concomitantes con este principio activo:")
            selec_useright = dataframe_with_selections(dfopciones_medmas)
        else:
            st.write("")
    # Mostrar mensaje si se seleccionan más de un medicamento
    if ((len(selec_userleft) >= 1 and len(selec_useright) >= 1) or len(selec_userleft) > 1 or
            len(selec_useright) > 1):
        st.error("Seleccione un solo medicamento")
    # Definir la selección final, para utilizar luego
    final_selection = pd.DataFrame()
    if len(selec_userleft) == 1 and len(selec_useright) == 0:
        final_selection = selec_userleft
    elif len(selec_userleft) == 0 and len(selec_useright) == 1:
        final_selection = selec_useright
    if len(final_selection) > 0:
        # Obtener el pa y atc del fármaco seleccionado (para unirlo con las otras tablas)
        atc_selected, pa_selected = final_selection["Código ATC"].iloc[0], final_selection["Principios Activos"].iloc[0]
        # Obtener el RxNorm con el API:
        rxnormid_api = get_rxcui(atc_selected)
        return pa_selected, atc_selected, rxnormid_api
    else:  # si no hay selección
        return None, None, None


def find_english_name(paselected_espa, atcselected_espa, rxnormid_api, atc_ema, paselected_ema):
    """Encuentra el nombre del medicamento seleccionado en inglés utilizando diferentes maneras
    Recibe:
    paselected_espa (str): principio activo del medicamento en español (CIMA).
    atc_selected (str): código atc del medicamento.
    rxnormid_api (str): código RxNorm del medicamento, None si no lo tiene.
    atc_ema (lista): lista de objetos de medicamentos de EMA que coinciden con la seleccionada (y CIMA).
    paselected_ema (str): principio activo del medicamento en inglés (EMA).
    Devuelve:
    atc_ema (lista): lista de objetos de medicamentos de EMA que coinciden con el seleccioncado (y CIMA).
    paselected_ema (str): principio activo del medicamento en inglés (EMA).
    selected_drug_gkb (lista): lista de objetos de PharmGKB que coinciden con el seleccionado.
    """
    if len(atc_ema) == 1:  # Si solo hay un medicamento con ese ATC
        try:
            paselected_ema = atc_ema[0].active_substance_ema
        except (Exception, ):
            pass
    # Si hay mas de un fármaco con ATC =, se comprueba si el pa es el mismo, si es así se coge ese nombre
    else:
        actives_substances_set = set()
        actives_substances_list = []
        for name in atc_ema:
            actives_substances_set.add(name.active_substance_ema)
            actives_substances_list.append(name.active_substance_ema)
        # Si solo hay un nombre con ese ATC, se coge
        if len(actives_substances_set) == 1:
            paselected_ema = (list(actives_substances_set))[0]
        # Si hay + de uno, se comproba que haya repetidos los nombres y si hay se coge el que mas se repite
        elif len(actives_substances_set) < len(actives_substances_list):
            most_common_substance = max(actives_substances_list, key=actives_substances_list.count)
            paselected_ema = most_common_substance

    # 1.- Con el nombre en inglés (EMA) y en castellano(CIMA), rxnorm y atc
    selected_drug_gkb = session.query(DrugsGkb).filter(DrugsGkb.rxnorm_identifiers_gkb == rxnormid_api,
                                                       DrugsGkb.atc_identifiers_gkb == atcselected_espa, or_
                                                       (DrugsGkb.name_gkb == paselected_ema,
                                                        DrugsGkb.generic_name_gkb == paselected_ema,
                                                        DrugsGkb.trade_name_gkb == paselected_ema,
                                                        DrugsGkb.name_gkb == paselected_espa,
                                                        DrugsGkb.generic_name_gkb == paselected_espa,
                                                        DrugsGkb.trade_name_gkb == paselected_espa)).all()
    # 2.- Si no se encuentra, se hace con rxnorm y atc
    if len(selected_drug_gkb) == 0:
        selected_drug_gkb = session.query(DrugsGkb).filter(
            DrugsGkb.rxnorm_identifiers_gkb == rxnormid_api,
            DrugsGkb.atc_identifiers_gkb == atcselected_espa).all()
        # 3.- Con atc y nombre en ingles+cast
        if len(selected_drug_gkb) == 0:
            selected_drug_gkb = session.query(DrugsGkb).filter(
                DrugsGkb.atc_identifiers_gkb == atcselected_espa, or_(DrugsGkb.name_gkb == paselected_ema,
                                                                      DrugsGkb.generic_name_gkb == paselected_ema,
                                                                      DrugsGkb.trade_name_gkb == paselected_ema,
                                                                      DrugsGkb.name_gkb == paselected_espa,
                                                                      DrugsGkb.generic_name_gkb == paselected_espa,
                                                                      DrugsGkb.trade_name_gkb == paselected_espa)).all()
            # 4- Con el nombre en ingles+cast y Rxnorm:
            if len(selected_drug_gkb) == 0:
                selected_drug_gkb = (session.query(DrugsGkb).filter(
                    DrugsGkb.rxnorm_identifiers_gkb == rxnormid_api, or_(DrugsGkb.name_gkb == paselected_ema,
                                                                         DrugsGkb.generic_name_gkb ==
                                                                         paselected_ema,
                                                                         DrugsGkb.trade_name_gkb ==
                                                                         paselected_ema,
                                                                         DrugsGkb.name_gkb == paselected_espa,
                                                                         DrugsGkb.generic_name_gkb == paselected_espa,
                                                                         DrugsGkb.trade_name_gkb == paselected_espa)).
                                     all())
                # 5.- Con el nombre en ingles+cast
                if len(selected_drug_gkb) == 0:
                    selected_drug_gkb = session.query(DrugsGkb).filter(
                        or_(DrugsGkb.name_gkb == paselected_ema,
                            DrugsGkb.generic_name_gkb == paselected_ema,
                            DrugsGkb.trade_name_gkb == paselected_ema,
                            DrugsGkb.name_gkb == paselected_espa,
                            DrugsGkb.generic_name_gkb == paselected_espa,
                            DrugsGkb.trade_name_gkb == paselected_espa)).all()
                    # 6.- Con solo ATC
                    if len(selected_drug_gkb) == 0:
                        selected_drug_gkb = session.query(DrugsGkb).filter(
                            DrugsGkb.atc_identifiers_gkb == atcselected_espa).all()
                        # 7.- Con solo Rxnorm
                        if len(selected_drug_gkb) == 0:
                            selected_drug_gkb = session.query(DrugsGkb).filter(
                                DrugsGkb.rxnorm_identifiers_gkb == rxnormid_api).all()

    return atc_ema, paselected_ema, selected_drug_gkb


def get_panelesp_info(pa_selected):
    """Obtener indicaciones desde el panel genético de españa, que coinciden con el principio activo seleccionado.
    Recibe el principio activo seleccionado.
    Devuelve una lista de diccionarios con las indicaciones si coinciden con el principio activo"""
    data_panel = []
    # Pasar a una lista si solo hay un objeto y hay mas de una dividirlo
    pa_lista = [pa_selected] if ", " not in pa_selected else pa_selected.split(", ")
    for pa in pa_lista:
        pa_new_panel = session.query(PanelGeneticoEsp).filter(PanelGeneticoEsp.farmaco_esp == pa).all()
        if pa_new_panel:
            for panel_object in pa_new_panel:
                data_panel.append({
                    'Patología': panel_object.patologia_esp,
                    'Fármaco': panel_object.farmaco_esp,
                    'Gen o regiones a estudiar': panel_object.gen_esp,
                    'Observaciones': panel_object.observaciones_esp})
    return data_panel


def get_unique_genes_variants(df_column):
    """Obtiene los valores únicos de una columna de un DataFrame.
    Elimina los valores nulos, divide los valores compuestos separados por comas y filtra por valores únicos.
    Recibe una columna de un dataframe.
    Devuelve una lista con valores únicos de la columna."""
    elementos_unicos = df_column.dropna().unique()
    elementos_procesados = []
    for element in elementos_unicos:   # Elemento: puede tener mas de un valor
        subelementos = [e.strip() for e in element.split(',')]
        elementos_procesados.extend(subelementos)
    final_unicos = list(set(elementos_procesados))
    return final_unicos


def dataframe_with_selections_url(df):
    """Muestra un DataFrame con opción de selecionar filas y una URL clicable.
    Recibe un DataFrame.
    Dvuelve un DataFrame con las filas seleccionadas"""
    df_with_selections = df.copy()
    df_with_selections.insert(0, "Seleccionar", False)  #
    edited_df = st.data_editor(df_with_selections, hide_index=True,
                               column_config={"Seleccionar": st.column_config.CheckboxColumn(required=True),
                                              "URL": st.column_config.LinkColumn(
                                                  "URL", display_text="PharmGKB")}, disabled=df.columns,)
    selected_rows = edited_df[edited_df.Seleccionar]
    return selected_rows.drop('Seleccionar', axis=1)


def get_allele_info(id_input):
    """Obtiene las indicaciones de alelos y los genotipos que tienen indicaciones.
    Recibe el id de la anotación clínica.
    Devuelve una tuple que contiene un dataframe con la información de alelos correspondiente al id y una lista con
     los genotipos que contienen indicaiones."""
    ann_alleles = session.query(ClinicalAnnAlleles).filter(
        ClinicalAnnAlleles.clinical_annotation_id_alleles == id_input).all()
    an_allele_indications = []
    all_genotipes_windications = []
    for label in ann_alleles:
        all_genotipes_windications.append(label.genotype_alleles)
        an_allele_indications.append({
            'ID de Anotación Clínica': label.clinical_annotation_id_alleles,
            'Genotipo/Alélo': label.genotype_alleles,
            'Texto de Anotación': label.annotation_text_alleles,
            'Función del Alélo': label.allele_function, })
    all_genotipes_windications = [elemento.upper() for elemento in all_genotipes_windications]
    df_allele_indications = pd.DataFrame(an_allele_indications)
    return df_allele_indications, all_genotipes_windications


def get_ddi(pa_selected, paselected_ema, name_drug_gkb, pa_all_selected):
    """Obtiene información de interacciones fármaco-fármaco para un principio activo seleccionado.
    Recibe: el principio activo seleccionado en castellano, el principio activo seleccionado en inglés y
    una lista de todos los princpios activos.
    Devuelve:
    - ddi_existe: un booleano que indica si existen o no interacciones fármaco-fármaco para el principio activo.
    - df_interacciones: un DataFrame que contiene las interacciones.
    - ddi_concomi: una lista de diccionarias para fármacos concomitantes, donde
    la clave es el principio activo y el valor las interacciones en un DataFrame."""
    ddi_concomi = []
    df_interacciones = []
    ddi_existe = False
    if "," not in paselected_ema:
        ddi = session.query(DrugDrugInteractions).filter(or_(DrugDrugInteractions.drug_1 == paselected_ema,
                                                             DrugDrugInteractions.drug_2 == paselected_ema,
                                                             DrugDrugInteractions.drug_1 == pa_selected,
                                                             DrugDrugInteractions.drug_2 == pa_selected,
                                                             DrugDrugInteractions.drug_1 == name_drug_gkb,
                                                             DrugDrugInteractions.drug_2 == name_drug_gkb
                                                             )).all()
        if ddi:
            dd_interactions = []
            for interaction in ddi:
                dd_interactions.append({'Fármaco 1': interaction.drug_1, 'Fármaco 2': interaction.drug_2,
                                        'Gravedad': interaction.level_ddi})
            if len(dd_interactions) > 0:
                # Si hay ddi interacciones, se obtiene el df y se recoloca
                ddi_existe = True
                paselected_ema_list = [paselected_ema, pa_selected]
                dd_interactions_df = pd.DataFrame(dd_interactions)
                # Filas donde el fármaco seleccionado está en Fármaco 1
                interactions1 = dd_interactions_df[dd_interactions_df["Fármaco 1"].isin(paselected_ema_list)]
                df_interactions1 = interactions1.loc[:, ["Fármaco 2", "Gravedad"]]
                df_interactions1.rename(columns={"Fármaco 2": "Interacciones"}, inplace=True)
                # Filas donde el fármaco seleccionado está en Fármaco 2
                interactions2 = dd_interactions_df[dd_interactions_df["Fármaco 2"].isin(paselected_ema_list)]
                df_interacciones2 = interactions2.loc[:, ["Fármaco 1", "Gravedad"]]
                df_interacciones2.rename(columns={"Fármaco 1": "Interacciones"}, inplace=True)
                df_interacciones = pd.concat([df_interactions1, df_interacciones2], ignore_index=True)
                df_interacciones.drop_duplicates()

    else:  # Si hay mas de un principio activo, se buscan ddi para cada uno
        if pa_all_selected is None:  # Para la funcionalidad 1
            pa_iterar = paselected_ema.split(", ")
            pa_selected = pa_selected.split(", ")
            name_drug_gkb = name_drug_gkb.split(", ")
            pa_iterar = list(set(pa_iterar + pa_selected + name_drug_gkb))
        else:   # Para la funcionalidad 3
            ddi_concomi = []
            pa_iterar = pa_all_selected
        for pa in pa_iterar:
            dd_interactions = []
            ddi = session.query(DrugDrugInteractions).filter(or_(DrugDrugInteractions.drug_1 == pa,
                                                                 DrugDrugInteractions.drug_2 == pa)).all()
            if ddi:
                for interaction in ddi:
                    dd_interactions.append({'Fármaco 1': interaction.drug_1, 'Fármaco 2': interaction.drug_2,
                                            'Gravedad': interaction.level_ddi})
            if len(dd_interactions) > 0:
                ddi_existe = True
                dd_interactions_df = pd.DataFrame(dd_interactions)
                interactions1 = dd_interactions_df[dd_interactions_df["Fármaco 1"] == pa]
                df_interactions1 = interactions1.loc[:, ["Fármaco 2", "Gravedad"]]
                df_interactions1.rename(columns={"Fármaco 2": "Interacciones"}, inplace=True)
                interactions2 = dd_interactions_df[dd_interactions_df["Fármaco 2"] == pa]
                df_interacciones2 = interactions2.loc[:, ["Fármaco 1", "Gravedad"]]
                df_interacciones2.rename(columns={"Fármaco 1": "Interacciones"}, inplace=True)
                df_interacciones = pd.concat([df_interactions1, df_interacciones2], ignore_index=True)
                df_interacciones.drop_duplicates()

                ddi_concomi.append({pa: df_interacciones})
    return ddi_existe, df_interacciones, ddi_concomi


def variantes_vcf(idpaciente):
    """Procesa un archivo VCF y obtiene las variantes genéticas para un paciente dado.
    Convierte los genotipos a un formato más legible.
    Recibe un identificador del paciente (str) cuyo archivo VCF se desea procesar.
    Devuelve;
    - Una lista de diccionarios, cada uno representando una variante genética con las claves: cromosoma,
        posición, id, el alelo de referencia, el alelo alternativo y el genotipo del paciente para esa variante.
    - En caso de error, devuelve un mensaje de error."""
    try:
        num_header = 0
        with open(f"data/patient_data/{idpaciente}.vcf") as file:
            for line in file:
                if line.startswith("##") or line.startswith("\"##"):
                    num_header += 1
                else:
                    break
        vcf = pd.read_csv(f"data/patient_data/{idpaciente}.vcf", sep="\t", skiprows=num_header,
                          encoding='ISO-8859-1')
    except (Exception,):
        variantes = "Este paciente no está registrado."
        return variantes
    try:
        # Procesar el archivo
        vcf = vcf[vcf["FILTER"] == "PASS"]
        variantes = []
        for record in vcf.iterrows():
            # Crear una lista de diccionarios donde se obtienen alelos de referencia y alelo alternativo
            dicc_numbers = []
            ref = record[1]['REF']
            dicc_numbers.append({0: ref})
            alt = (record[1]['ALT'])
            # Como puede haber más de un alelo alternativo, se añade cada uno
            if "," in alt:
                alt = alt.split(",")
            else:
                alt = [alt]
            for i, letra in enumerate(alt):
                # Se procesan casos que pueden dar (como <del>)
                if ">" in letra or "<" in letra:
                    letra = letra.replace("<", "").replace(">", "")
                dicc_numbers.append({i+1: letra})

            formato = record[1]['NA00001']  # La primera muestra
            gt = formato.split(":")[0]
            valor1 = int((re.split("[|/]", gt))[0])  # Alelo 1
            valor2 = int((re.split("[|/]", gt))[1])  # Alelo 2
            if valor1 == valor2:  # Es homocigoto
                for dicc in dicc_numbers:
                    if valor1 in dicc:
                        if len(dicc[valor1]) == 1:  # El alelo es solo de una letra
                            gt = dicc[valor1]*2
                        else:  # Alelo múltiple, se añade /
                            gt = dicc[valor1] + "/" + dicc[valor1]
                gt = [gt]
            else:  # Es heterocigoto  (crear una lista => ["CT","TC"])
                # Pasar la lista de diccionarios a un diccionario
                dicc_final = {}
                for dicc in dicc_numbers:
                    dicc_final.update(dicc)
                # Obtener los alelos correspondientes a los valores del genotipo del paciente
                gt = []
                genot1 = dicc_final.get(valor1)
                genot2 = dicc_final.get(valor2)
                if len(genot1) > 1 or len(genot2) > 1:
                    gt_element = genot1 + "/" + genot2
                    gt_element2 = genot2 + "/" + genot1
                else:
                    gt_element = genot1 + genot2
                    gt_element2 = genot2 + genot1
                gt.append(gt_element)
                gt.append(gt_element2)
            # El gt será una lista. En el caso de heterocigotos, con una longitud mayor que uno.
            variantes.append(
                {"chrom": record[1]['#CHROM'],
                 "Position": record[1]['POS'],
                 'ID': record[1]['ID'],
                 "Ref": record[1]['REF'],
                 "Alt": record[1]['ALT'],
                 "Genotipo": gt
                 })
    except (Exception,):
        variantes = "Ha ocurrido un error al procesar el archivo."
    return variantes
