import pandas as pd
import os

def leer_columnas_csv(ruta_del_archivo: str) -> tuple[list, list]:
    """
    Lee un archivo CSV y extrae los valores de las columnas 'Title' y 'Link'.

    Args:
        ruta_del_archivo (str): La ruta al archivo CSV.

    Returns:
        tuple[list, list]: Una tupla conteniendo dos listas: (titulos, links).
                           Devuelve listas vacías si hay un error.
    """
    titulos = []
    links = []

    # Verificamos que el archivo exista antes de intentar leerlo
    if not os.path.exists(ruta_del_archivo):
        print(f"❌ Error: El archivo no fue encontrado en la ruta: {ruta_del_archivo}")
        return titulos, links

    try:
        # Leemos el archivo CSV usando pandas
        dataframe = pd.read_csv(ruta_del_archivo)

        # Verificamos que las columnas existan
        if 'Title' in dataframe.columns and 'Link' in dataframe.columns:
            # Convertimos las columnas del dataframe a listas
            titulos = dataframe['Title'].tolist()
            links = dataframe['Link'].tolist()
            print("✅ Archivo CSV leído y procesado exitosamente.")
        else:
            print("❌ Error: El CSV no contiene las columnas requeridas ('Title' y 'Link').")

    except Exception as e:
        print(f"❌ Ocurrió un error inesperado al leer el archivo: {e}")

    return titulos, links