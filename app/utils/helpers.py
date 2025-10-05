import pandas as pd
import os

def buscar_correspondencia_pandas(df: pd.DataFrame, title: str = None, link: str = None):
    """
    Busca de forma eficiente usando la indexación booleana de Pandas.
    """
    try:
        if title:
            # Filtra el DataFrame donde el título coincide
            resultado = df[df['Title'] == title]
            if not resultado.empty:
                # Devuelve el primer link encontrado
                return resultado['Link'].iloc[0]
        
        elif link:
            # Filtra el DataFrame donde el link coincide
            resultado = df[df['Link'] == link]
            if not resultado.empty:
                # Devuelve el primer título encontrado
                return resultado['Title'].iloc[0]

    except KeyError:
        print("❌ Error: Columnas 'Title' o 'Link' no encontradas.")
    
    return None # Si no se encuentra nada

def leer_columnas_csv(ruta_del_archivo: str, title: str = None, link: str = None) -> tuple[list, list]:
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
            if title:
                return buscar_correspondencia_pandas(dataframe,title=title)
            if link:
                return buscar_correspondencia_pandas(dataframe,link=link)        
            print("✅ Archivo CSV leído y procesado exitosamente.")
        else:
            print("❌ Error: El CSV no contiene las columnas requeridas ('Title' y 'Link').")

    except Exception as e:
        print(f"❌ Ocurrió un error inesperado al leer el archivo: {e}")

    return titulos, links