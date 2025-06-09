import bcrypt
import getpass
import os
import json
from cryptography.fernet import Fernet
from Modelo.models import AdminUser

UserPrincipal = "DBusers.json"

ruta_carpeta = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "DBwroser")

# Funcionn  generar usuario y Contraseña Principal
def generar_Admin():
    #Verificacion la carpeta del destino existe si no se crea
    if not os.path.exists(ruta_carpeta):
        os.makedirs(ruta_carpeta)

    #ruta completa para el archvio Json dentro de data
    ruta_archivo = os.path.join(ruta_carpeta, UserPrincipal)

    if not os.path.exists(ruta_archivo):
        NombreAdmin = input("Ingrese su nombre de usuario: ")
        password = getpass.getpass("Ingrese su contraseña: ")
        hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
        password = hashed.decode('utf-8')

        # se crea el objeto admiuser con sus datos previos insertados
        nuevoadmin = AdminUser(
            username= NombreAdmin,
            ContresañUser = password
        )

        with open(ruta_archivo, "w") as file:
            json.dump(nuevoadmin.dict(), file,indent=4)

        print(f"El archvio se creo correctamente en : {ruta_archivo}")
    else:
        print(f"El archivo de usuario ya existe en: {ruta_archivo}")
    