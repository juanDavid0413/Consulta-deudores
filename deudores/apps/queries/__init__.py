def __init__(self):
        gc = gspread.service_account(filename=settings.GOOGLE_SHEETS_CREDENTIALS_FILE)
        sh = gc.open_by_key(settings.GOOGLE_SHEET_ID)

        self.ws_bd_facturacion = sh.worksheet("BD_FACTURACION")
        self.ws_bd2 = sh.worksheet("BD2")
        self.ws_bd3 = sh.worksheet("BD3")

        # Al cargar, convertimos todas las llaves a minúsculas y sin espacios
        self.bd_facturacion = [{k.strip().lower(): v for k, v in r.items()} for r in self.ws_bd_facturacion.get_all_records()]
        self.bd2 = [{k.strip().lower(): v for k, v in r.items()} for r in self.ws_bd2.get_all_records()]
        self.bd3 = [{k.strip().lower(): v for k, v in r.items()} for r in self.ws_bd3.get_all_records()]