import requests
from django.conf import settings

class WisproInvoicesService:
    BASE_URL = "https://www.cloud.wispro.co/api/v1"
    AUTH_TOKEN = getattr(settings, 'WISPRO_AUTH_TOKEN', None)

    @classmethod
    def consultar_todo(cls, cedula):
        headers = {
            "Authorization": cls.AUTH_TOKEN,
            "Accept": "application/json"
        }
        cedula_limpia = str(cedula).strip()
        
        # Inicializamos la estructura de respuesta
        resultado = {
            "existe": False,
            "nombre": None,
            "tiene_contratos": False,
            "contratos": [],
            "en_mora": False,
            "facturas": [],
            "total_deuda": 0,
            "estado_final": "SIN_REGISTRO" # POSITIVO, NEGATIVO, SIN_REGISTRO
        }

        try:
            # 1. BUSCAR CLIENTE para obtener el Nombre
            client_params = {"national_identification_number_eq": cedula_limpia}
            r_client = requests.get(f"{cls.BASE_URL}/clients", headers=headers, params=client_params, timeout=10)
            
            if r_client.status_code == 200 and r_client.json().get("data"):
                cliente = r_client.json()["data"][0]
                resultado["existe"] = True
                resultado["nombre"] = cliente.get("name")
            else:
                return resultado # Si no existe el cliente, terminamos aquí

            # 2. BUSCAR CONTRATOS
            contract_params = {"client_national_identification_number_eq": cedula_limpia}
            r_contract = requests.get(f"{cls.BASE_URL}/contracts", headers=headers, params=contract_params, timeout=10)
            
            if r_contract.status_code == 200:
                contratos_data = r_contract.json().get("data", [])
                for c in contratos_data:
                    resultado["contratos"].append({
                        "public_id": c.get("public_id"),
                        "estado": c.get("state"),
                        "plan": c.get("plan_name") # Si la API lo incluye, sino usar ID
                    })
                resultado["tiene_contratos"] = len(resultado["contratos"]) > 0

            # 3. BUSCAR FACTURAS
            invoice_params = {"client_national_identification_number_eq": cedula_limpia}
            r_invoice = requests.get(f"{cls.BASE_URL}/invoicing/invoices", headers=headers, params=invoice_params, timeout=10)
            
            if r_invoice.status_code == 200:
                facturas_data = r_invoice.json().get("data", [])
                for inv in facturas_data:
                    balance = float(inv.get("balance") or 0)
                    if balance > 0:
                        resultado["facturas"].append({
                            "numero": inv.get("invoice_number"),
                            "saldo": balance,
                            "vencimiento": inv.get("first_due_date")
                        })
                        resultado["total_deuda"] += balance
                resultado["en_mora"] = len(resultado["facturas"]) > 0

            # 4. LÓGICA DE VALIDACIÓN FINAL
            # NEGATIVO si: Tiene contratos O tiene facturas con deuda
            if resultado["tiene_contratos"] or resultado["en_mora"]:
                resultado["estado_final"] = "NEGATIVO"
            # POSITIVO si: Existe el cliente PERO NO tiene contratos ni facturas
            elif resultado["existe"]:
                resultado["estado_final"] = "POSITIVO"

            return resultado

        except Exception as e:
            print(f"Error Wispro: {e}")
            return resultado