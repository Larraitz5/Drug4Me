import os
import datetime as dt
from db_funciones import read_json_file
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import declarative_base

# Configurar engine, path, session
properties = read_json_file("properties/properties.json")


def get_current_version():
    """Obtiene la versión más reciente de la base de datos.
    Devuelve "0" si no existe ninguna base de datos. Si existe, devuelve la siguiente versión como una cadena."""
    db_path = properties["database_path"]
    db_list = [file for file in os.listdir(db_path) if os.path.splitext(file)[-1] == ".db"]
    if len(db_list) == 0:
        return str(0)
    else:
        versions = [int(elem.split("_")[2][1:]) for elem in db_list]
        return str(max(versions))


def get_last_db_name():
    """Obtiene el nombre de la base de datos más reciente.
    Si no existe la base de datos, se establece la versión en 0 y se devuelve un nombre
     para la base de datos con la fecha actual.
    Si se encuentra una versión, devuelve el nombre de la base de datos de esa versión."""
    db_path = properties["database_path"]
    db_list = [file for file in os.listdir(db_path) if os.path.splitext(file)[-1] == ".db"]
    version = get_current_version()
    if version != "0" or (version == "0" and len(db_list) != 0):
        db_list = [file for file in os.listdir(db_path) if file.startswith(f"bd_Drug4Me_v{version}_")]
        if db_list:
            return max(db_list, key=lambda x: x.split("_")[-1].split(".")[0])
    current_date_and_time = dt.datetime.now()
    date_str = current_date_and_time.strftime("%Y%m%d")
    return f"bd_Drug4Me_v{version}_{date_str}.db"


# Crear conexión a la bd con la última versión
engine = create_engine(f"sqlite:///{os.path.join(properties['database_path'], get_last_db_name())}", echo=True)

# Crear la base declarativa para definir las tablas
Base = declarative_base()

# Crear sesion para insertar los datos a la bd
Session = sessionmaker(bind=engine)
session = Session()
