from django.shortcuts import render
from .forms import ConsultaCedulaForm
from .services.google_sheets_service import GoogleSheetsDebtorsService
from .services.wispro_invoices_service import WisproInvoicesService
from .forms import ConsultaCedulaForm
from django.core.mail import send_mail
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.utils.html import strip_tags

def consulta_deudor_view(request):
    form = ConsultaCedulaForm(request.POST or None)
    results = None

    if request.method == "POST" and form.is_valid():
        cedula = form.cleaned_data["cedula"]
        
        # 1. Llamada al nuevo método unificado de Wispro
        wispro_data = WisproInvoicesService.consultar_todo(cedula)

        # 2. Servicio Google Sheets (se mantiene igual)
        gs_service = GoogleSheetsDebtorsService()
        data_facturacion = gs_service.bd_facturacion_por_cedula(cedula)
        data_bd2 = gs_service.bd2_por_cedula(cedula)
        #data_bd3 = gs_service.bd3_por_cedula(cedula)

        total_facturacion = sum(item['saldo'] for item in data_facturacion)
        total_bd2 = 0
        for item in data_bd2:
            try:
                valor = float(str(item['monto']).replace(',', '').replace('.', ''))
                total_bd2 += valor
            except: continue

# 1. Wispro es "Apto" si: 
    #    A. El estado es POSITIVO (existe pero no debe nada)
    #    B. O si el cliente NO EXISTE en Wispro (no tiene registros)
        wispro_apto = (
            wispro_data.get('estado_final') == "POSITIVO" or 
            not wispro_data.get('existe')
        )

        # 2. Las hojas de cálculo son "Aptas" si están vacías
        no_hay_en_facturacion = len(data_facturacion) == 0
        no_hay_en_bd2 = len(data_bd2) == 0

        # 3. Lógica de Aptitud Final
        # Es APTO si Wispro está limpio Y no hay nada en las hojas de Google
        es_apto = wispro_apto and no_hay_en_facturacion and no_hay_en_bd2

        def enviar_notificacion_denegado(usuario_sistema, cedula_cliente, nombre_cliente):
            subject = f"🚫 ALERTA DE SEGURIDAD: Trámite Denegado - {cedula_cliente}"
            
            # Versión HTML con diseño corporativo
            html_content = f"""
            <html>
            <body style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; color: #692A86; line-height: 1.6; background-color: #f4f4f4; padding: 20px;">
                <div style="max-width: 600px; margin: 0 auto; background: #ffffff; border-radius: 8px; overflow: hidden; border: 1px solid #e0e0e0; box-shadow: 0 4px 10px rgba(0,0,0,0.1);">
                    <div style="background-color: #692A86; padding: 20px; text-align: center;">
                        <h1 style="color: #ffffff; margin: 0; font-size: 24px; letter-spacing: 2px;">VELONET</h1>
                        <p style="color: #ffffff; margin: 5px 0 0; font-size: 12px; text-transform: uppercase;">Sistema de Control de Deudores</p>
                    </div>
                    
                    <div style="padding: 30px;">
                        <h2 style="color: #d9534f; margin-top: 0; border-bottom: 2px solid #f8d7da; padding-bottom: 10px;">Notificación de Trámite Denegado</h2>
                        <p>Se ha detectado una consulta de un cliente con <strong>obligaciones pendientes</strong>. El sistema ha denegado el trámite.</p>
                        
                        <table style="width: 100%; border-collapse: collapse; margin: 20px 0;">
                            <tr>
                                <td style="padding: 10px; background: #f9f9f9; border: 1px solid #eee; font-weight: bold; width: 40%;">Nombre del Cliente:</td>
                                <td style="padding: 10px; border: 1px solid #eee;">{nombre_cliente}</td>
                            </tr>
                            <tr>
                                <td style="padding: 10px; background: #f9f9f9; border: 1px solid #eee; font-weight: bold;">Cédula/ID:</td>
                                <td style="padding: 10px; border: 1px solid #eee;">{cedula_cliente}</td>
                            </tr>
                            <tr>
                                <td style="padding: 10px; background: #f9f9f9; border: 1px solid #eee; font-weight: bold;">Consultado por:</td>
                                <td style="padding: 10px; border: 1px solid #eee;">{usuario_sistema}</td>
                            </tr>
                            <tr>
                                <td style="padding: 10px; background: #f9f9f9; border: 1px solid #eee; font-weight: bold;">Estado Final:</td>
                                <td style="padding: 10px; border: 1px solid #eee; color: #d9534f; font-weight: bold;">NO APTO</td>
                            </tr>
                        </table>
                        
                        <div style="background-color: #fff3cd; border-left: 5px solid #ffecb5; padding: 15px; margin: 20px 0; color: #856404; font-size: 14px;">
                            <strong>Nota del Sistema:</strong> El prospecto no cumple con las políticas crediticias de Velonet debido a registros en bases de datos internas o facturación pendiente en Wispro.
                        </div>
                    </div>
                    
                    <div style="background-color: #f8f9fa; padding: 15px; text-align: center; font-size: 12px; color: #692A86; border-top: 1px solid #eee;">
                        Este es un mensaje automático generado por el Portal de Consultas Velonet.<br>
                        Por favor, no responda a este correo.
                    </div>
                </div>
            </body>
            </html>
            """
            
            text_content = strip_tags(html_content) # Versión en texto plano para dispositivos viejos
            
            email = EmailMultiAlternatives(
                subject,
                text_content,
                settings.EMAIL_HOST_USER,
                ['ju99da04ca13va@gmail.com']             )
            email.attach_alternative(html_content, "text/html")
            
            try:
                email.send()
            except Exception as e:
                print(f"Error enviando correo HTML: {e}")

        if not es_apto:
            # 1. Intentamos sacar el nombre de Wispro
            nombre_cliente = wispro_data.get('nombre')

            # 2. Si Wispro no tiene nombre (cliente nuevo), buscamos en Google Sheets
            if not nombre_cliente or nombre_cliente == "None":
                if data_facturacion:
                    nombre_cliente = data_facturacion[0].get('nombre')
                elif data_bd2:
                    nombre_cliente = data_bd2[0].get('nombre')
            #nombre_cliente = wispro_data.get('nombre', 'Nombre no disponible')
            enviar_notificacion_denegado(
                usuario_sistema=request.user.username,
                cedula_cliente=cedula,
                nombre_cliente=nombre_cliente
            )        

        results = {
            'wispro': wispro_data,
            'bd_facturacion': data_facturacion,
            'total_bd_facturacion': total_facturacion,
            'bd2': data_bd2,
            'total_bd2': total_bd2,
            #'bd3': data_bd3,
            'es_apto': es_apto
        }

    return render(request, "queries/queries_form.html", {"form": form, "results": results})


