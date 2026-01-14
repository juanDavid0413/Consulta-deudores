import pandas as pd
from django.shortcuts import render
from google.oauth2.service_account import Credentials
import gspread
from django.conf import settings
import re

def upload_bd2(request):
    if request.method == 'POST':
        try:
            file = request.FILES.get('file')
            if not file:
                return render(request, 'uploads/upload.html', {'error': 'No se seleccionó ningún archivo.'})

            # =========================
            # LEER ARCHIVO
            # =========================
            if file.name.endswith('.csv'):
                df = pd.read_csv(file)
            else:
                df = pd.read_excel(file)

            # =========================
            # VALIDAR COLUMNAS
            # =========================
            expected_columns = [
                "Número Documento Cliente",
                "Nombre Completo",
                "Valor Obligación"
            ]

            # Verificamos si las columnas esperadas existen en el archivo
            if not all(col in df.columns for col in expected_columns):
                return render(request, 'uploads/upload.html', {
                    'error': f'Estructura incorrecta. El archivo debe tener las columnas: {", ".join(expected_columns)}'
                })

            # Reordenamos el DF para asegurar que los datos entren en el orden correcto a Sheets
            df = df[expected_columns]

            # Limpieza de Cédulas (Evita el .0 en números grandes de Excel)
            df['Número Documento Cliente'] = df['Número Documento Cliente'].astype(str).apply(lambda x: x.split('.')[0] if '.' in x else x)

            # =========================
            # GOOGLE SHEETS
            # =========================
            creds = Credentials.from_service_account_file(
                settings.GOOGLE_SHEETS_CREDENTIALS_FILE,
                scopes=["https://www.googleapis.com/auth/spreadsheets"]
            )

            client = gspread.authorize(creds)
            sheet = client.open_by_key(settings.GOOGLE_SHEET_ID)
            worksheet = sheet.worksheet("BD2")

            # =========================
            # PROCESAR DATOS
            # =========================
            # Convertimos NaN a vacío y pasamos a lista
            values = df.fillna('').values.tolist()
            rows_to_add = len(values)

            # Obtenemos datos actuales para saber dónde empezar a escribir
            existing_data = worksheet.get_all_values()
            last_row_with_data = len(existing_data)
            start_row = last_row_with_data + 1

            # Agrandar hoja si es necesario
            current_rows_capacity = worksheet.row_count
            if start_row + rows_to_add - 1 > current_rows_capacity:
                rows_needed = (start_row + rows_to_add - 1) - current_rows_capacity
                worksheet.add_rows(rows_needed)

            # Insertar datos masivamente
            # Usamos el rango dinámico Ej: A10:C150
            end_row = start_row + rows_to_add - 1
            range_label = f"A{start_row}:C{end_row}"
            worksheet.update(range_label, values)

            # ÉXITO: Retornamos a la misma vista con la variable 'rows'
            return render(request, 'uploads/upload.html', {
                'rows': rows_to_add
            })

        except Exception as e:
            # ERROR: Retornamos a la misma vista con la variable 'error'
            print(f"Error en carga: {str(e)}")
            return render(request, 'uploads/upload.html', {
                'error': f'Error técnico: {str(e)}'
            })

    # Petición GET normal
    return render(request, 'uploads/upload.html')