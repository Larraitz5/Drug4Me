import os.path

from ddi_funciones_prospects import *
from ddi_ema_get_all_drugs import get_drugs

# Obtener una lista de todos los fármacos
all_drugs = get_drugs()

# Lista de palabras clave
palabras_a_buscar = ["decrease", "decreases", "decreased", "decreasing",
                     "increase", "increases", "increased", "increasing",
                     "lower", "lowers", "lowered", "lowering",
                     "higher", "highers", "highered", "highering",
                     "co-administration", "concurrent", "concomitant",
                     "combination", "interaction with"]


def initialize_folders():

    paths = read_json_file("EMA_DDI/properties_ema/properties_ema.json")["paths"]
    for path in paths:
        if not os.path.exists(path):
            os.makedirs(path)


if __name__ == "__main__":
    initialize_folders()
    # Descargar y obtener el excel de medicamentos desde el EMA y se itera sobre los medicamentos
    df_ema = get_ema_data()
    for index, row in df_ema.iterrows():
        url = row['URL']
        if index == 2:
            pass
        medicine_name_1 = row['Medicine_name']
        medicine_name = medicine_name_1.replace("/", "_").replace(":", "_")
        pa_1 = row['Active_substance']
        pa = pa_1.replace("/", "_").replace(":", "_").replace("\\", "_").strip().replace(" ", "")

        # Descargar y obtener prospectos mediante URL
        file_name_final = f"{index}_{medicine_name}.pdf"
        print(f"{index}: {file_name_final}")
        results = download_prosp(url, medicine_name, file_name_final)
        if results is not None:
            file_name_pdf, medicine_name_pdf = results

            # Preprocesar prospectos para obtener  la sección 4.5
            file_name_prepro_txt = f"{index}_{medicine_name_pdf}.txt"
            if file_name_pdf is not None and medicine_name_pdf is not None:
                results_prepross = get_45_prospects_section(file_name_pdf, file_name_prepro_txt, medicine_name_pdf)
                if results_prepross is not None:
                    file_name_prepro_45, medicine_name = results_prepross

                    # Procesar la sección 45 para obtener ddi
                    file_name_ddi_txt = f"{index}_{medicine_name}.txt"
                    interacciones = buscar_interacciones(file_name_prepro_45, file_name_ddi_txt, pa, medicine_name,
                                                         all_drugs, palabras_a_buscar)
