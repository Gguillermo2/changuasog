from core import autenticacion

def main():
        usuario = autenticacion.generar_Admin()
        print(f"El usuario generado es {usuario}")


if __name__ == "__main__":
        main()

