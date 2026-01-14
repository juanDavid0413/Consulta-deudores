import gspread
import re
from django.conf import settings

class GoogleSheetsDebtorsService:
    def __init__(self):
        try:
            # Una sola conexión limpia
            self.gc = gspread.service_account(filename=settings.GOOGLE_SHEETS_CREDENTIALS_FILE)
            self.sh = self.gc.open_by_key(settings.GOOGLE_SHEET_ID)
            
            # Cargamos las hojas como objetos, pero NO los datos todavía para evitar caché
            self.ws_facturacion = self.sh.worksheet("BD_FACTURACION")
            self.ws_bd2 = self.sh.worksheet("BD2")
            #self.ws_bd3 = self.sh.worksheet("BD3")
        except Exception as e:
            print(f"ERROR CRÍTICO CONEXIÓN GOOGLE SHEETS: {e}")

    def _limpiar_valor(self, val):
        """Limpia cualquier valor para dejar solo números (quita puntos, comas, espacios)"""
        if val is None: return ""
        # Quitamos todo lo que no sea número
        return re.sub(r'[^\d]', '', str(val).strip())

    def bd_facturacion_por_cedula(self, cedula):
        resultados = []
        # Limpiamos el objetivo: solo números y quitamos ceros a la izquierda
        # Ejemplo: "01047" -> "1047"
        target = str(cedula).strip().lstrip('0')
        
        try:
            # Traemos datos frescos
            datos = self.ws_facturacion.get_all_values() 
            print(f"--- BUSCANDO EN BD_FACTURACION: '{target}' ---")
            
            for i, fila in enumerate(datos):
                if i == 0 or len(fila) < 3: continue 
                
                # Limpiamos la cédula de la hoja de la misma forma (quitando ceros a la izquierda)
                cedula_hoja_raw = str(fila[2]).strip()
                cedula_hoja_limpia = cedula_hoja_raw.lstrip('0').split('.')[0] # Quita 0s y .0
                
                # Si el target está contenido en la cédula de la hoja o viceversa
                if target != "" and target == cedula_hoja_limpia:
                    nombre = fila[0]
                    saldo_raw = fila[1]
                    
                    try:
                        # Extraer solo números del saldo
                        saldo_clean = "".join(filter(str.isdigit, str(saldo_raw)))
                        saldo = float(saldo_clean) if saldo_clean else 0
                    except:
                        saldo = 0

                    if saldo > 0:
                        print(f" MATCH! Fila {i+1}: {nombre} (${saldo})")
                        resultados.append({
                            "nombre": nombre,
                            "saldo": saldo
                        })
            
            if not resultados:
                print(f" No se encontró nada para '{target}'")
                
        except Exception as e:
            print(f"ERROR: {e}")
            
        return resultados

    def bd2_por_cedula(self, cedula):
        resultados = []
        target = self._limpiar_valor(cedula)
        try:
            # get_all_records es cómodo para BD2 porque tiene muchos encabezados
            datos = self.ws_bd2.get_all_records()
            for fila in datos:
                cedula_hoja = self._limpiar_valor(fila.get("Número Documento Cliente"))
                if cedula_hoja == target and target != "":
                    valor_raw = str(fila.get("Valor Obligación") or "0")
                    # Limpiamos solo para visualización
                    valor_limpio = re.sub(r'[^\d]', '', valor_raw)
                    try:
                        monto_final = "{:,.0f}".format(float(valor_limpio))
                    except:
                        monto_final = valor_raw

                    resultados.append({
                        "nombre": fila.get("Nombre Completo"),
                        "monto": monto_final 
                    })
        except Exception as e:
            print(f"ERROR EN BD2: {e}")
        return resultados
            
    #def bd3_por_cedula(self, cedula):
    #    target = self._limpiar_valor(cedula)
    #    try:
    #        datos = self.ws_bd3.get_all_records()
    #        for fila in datos:
    #            cedula_hoja = self._limpiar_valor(fila.get("Número Documento Cliente"))
    #            if cedula_hoja == target and target != "":
    #                return fila
    #    except Exception as e:
    #        print(f"ERROR EN BD3: {e}")
    #    return None