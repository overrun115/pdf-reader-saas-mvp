import os
import pandas as pd

def consolidar_excels(directorio, archivo_salida):
    archivos = [f for f in os.listdir(directorio) if f.endswith('.xlsx')]
    dataframes = []
    for archivo in archivos:
        ruta = os.path.join(directorio, archivo)
        df = pd.read_excel(ruta)
        dataframes.append(df)
    if dataframes:
        df_consolidado = pd.concat(dataframes, ignore_index=True)
        df_consolidado.to_excel(archivo_salida, index=False)
        print(f"Consolidado guardado en: {archivo_salida}")
    else:
        print("No se encontraron archivos .xlsx en la carpeta.")

if __name__ == "__main__":
    carpeta = "/Users/leandrodebagge/Desktop/Compartido"
    salida = "consolidado.xlsx"
    consolidar_excels(carpeta, salida)
