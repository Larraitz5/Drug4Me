import os
import json
import requests
import urllib.request
from zipfile import ZipFile
from urllib.request import Request

# Funciones para insertar data en la bd


def read_json_file(file_path):
    """Lee un archivo JSON y devuelve los datos como un diccionario.
    Recibe la ruta al archivo JSON como un string.
    Devuelve el contenido del archivo como un diccionario."""
    with open(file_path, encoding="utf-8") as json_file:
        data = json.load(json_file)
    return data


def solicitud_downloadfile_url(url, file_path):
    """Solicita y descarga un archivo desde una URL y lo guarda en una ruta local.
    Recibe 2 parámetros, la URL del archivo a descargar y la ruta local donde se guardará el archivo descargado."""
    # Realizar la solicitud GET para descargar el archivo
    response = requests.get(url, verify=False)
    # Verificar si la solicitud fue exitosa
    if response.status_code == 200:
        # Guardar el contenido del archivo en un archivo local
        with open(file_path, "wb") as f:
            f.write(response.content)


def solicitud_downloadzip_url(url, save_path):
    """Solicita y descarga un archivo ZIP desde una URL, luego lo descomprime.
    Recibe 2 parámetros, la URL del ZIP a descargar y la ruta local donde se guardará el archivo ZIP descargado y
    descomprimido."""
    # Realizar la solicitud GET para descargar el archivo
    response = requests.get(url)
    # Verificar si la solicitud fue exitosa
    if response.status_code == 200:
        with open(save_path, 'wb') as f:
            f.write(response.content)
        # Llamar a la función download_url para descomprimir el archivo
        downloadzip_url(url, save_path)


def downloadzip_url(url, save_path):
    """Descarga un archivo ZIP desde una URL, lo descomprime  y elimina el archivo ZIP.
    Recibe 2 parámetros, la URL del ZIP a descargar y la ruta local donde se guardará el archivo ZIP descargado y
    descomprimido."""
    # Descargar el archivo desde la URL
    req = Request(url=url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req) as dl_file:
        with open(save_path, 'wb') as out_file:
            out_file.write(dl_file.read())
    # Descomprimir el archivo ZIP
    with ZipFile(save_path, 'r') as zObject:
        zObject.extractall(os.path.dirname(save_path))
    # Eliminar el archivo ZIP después de extraer
    os.remove(save_path)
