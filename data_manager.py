import pandas as pd
import requests
from io import BytesIO

# Enlace directo al archivo en Google Sheets (puedes mover esto a un archivo config.json si lo prefieres)
GOOGLE_SHEETS_URL = "https://docs.google.com/spreadsheets/d/1-ph_TSfZQL2PFHlmuR--T2_C32JP9TJQ/export?format=xlsx"

# Función para descargar los datos desde Google Sheets
def descargar_datos():
    try:
        response = requests.get(GOOGLE_SHEETS_URL, timeout=10)
        response.raise_for_status()

        excel_data = BytesIO(response.content)
        cartera_df = pd.read_excel(excel_data, sheet_name='CARTERA')
        vencimientos_df = pd.read_excel(excel_data, sheet_name='VENCIMIENTOS')

        return cartera_df, vencimientos_df
    except requests.exceptions.RequestException as e:
        raise Exception(f"Error al descargar el archivo: {e}")

# Función para obtener los vencimientos futuros por SAIDS
def obtener_vencimientos_futuros(cartera_df, vencimientos_df):
    # Convertir las fechas a formato datetime
    vencimientos_df['Vencimiento'] = pd.to_datetime(vencimientos_df['Vencimiento'], errors='coerce')

    # Filtrar solo los vencimientos de 2024 y fechas futuras
    vencimientos_futuros = vencimientos_df[
        (vencimientos_df['Vencimiento'].dt.year == 2024) & 
        (vencimientos_df['Vencimiento'] > pd.Timestamp.now())
    ]

    # Crear un diccionario de vencimientos por SAIDS
    vencimientos_por_saids = {}
    for _, row in cartera_df.iterrows():
        saids = row['CODIGO_SAIDS']
        denominacion = row['DENOMINACION_SEGUN_POA']

        # Buscar el vencimiento más cercano para este SAIDS
        vencimiento_cercano = vencimientos_futuros[vencimientos_futuros['SAIDS'] == saids]['Vencimiento'].min()

        if not pd.isna(vencimiento_cercano):
            vencimientos_por_saids[denominacion] = vencimiento_cercano.strftime('%d/%m/%Y')

    return vencimientos_por_saids
