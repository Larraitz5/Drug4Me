import json
import requests


def read_json_file2(file_path):
    """Lee un archivo JSON y devuelve los datos como un diccionario.
    Recibe la ruta al archivo JSON como un string.
    Devuelve el contenido del archivo como un diccionario."""
    with open(file_path, encoding="utf-8") as json_file:
        data = json.load(json_file)
    return data


def solicitud_downloadfile_url(url, file_path):
    """Solicita y descarga un archivo desde una URL y lo guarda en una ruta local.
        Recibe 2 parámetros, la URL del archivo a descargar y la ruta local donde se guardará el archivo descargado.
        Devuelve True si la descarga fue exitosa, None si ocurrió algún error."""
    try:
        # Realizar la solicitud GET para descargar el archivo
        response = requests.get(url, verify=False)

        # Verificar si la solicitud fue exitosa (código de estado 200)
        if response.status_code == 200:
            # Guardar el contenido del archivo en un archivo local (escritura binaria. Si ya existe, se sobreescribe)
            with open(file_path, "wb") as f:
                f.write(response.content)
            return True
        else:
            return None
    except (Exception,):
        return None
