import pandas as pd
from django.shortcuts import render
from google.oauth2.service_account import Credentials
import gspread
from django.conf import settings


def upload_bd2(request):
    if request.method == 'POST':
        file = request.FILES['file']

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

        if list(df.columns) != expected_columns:
            return render(request, 'uploads/error.html', {
                'error': 'Las columnas del archivo no coinciden con BD2'
            })

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
        # FILA VACÍA
        # =========================
        values = df.fillna('').values.tolist()
        rows_to_add = len(values)

        # Filas actuales de la hoja
        current_rows = worksheet.row_count

        # Última fila con datos
        last_row_with_data = len(worksheet.get_all_values())

        # Fila donde inicia la inserción
        start_row = last_row_with_data + 1

        # Si la hoja no tiene filas suficientes, agrandarla
        if start_row + rows_to_add - 1 > current_rows:
            rows_needed = (start_row + rows_to_add - 1) - current_rows
            worksheet.add_rows(rows_needed)

        # Insertar datos
        worksheet.update(f"A{start_row}", values)


        return render(request, 'uploads/upload_success.html', {
            'rows': len(values)
        })

    return render(request, 'uploads/upload.html')
