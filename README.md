# 📡 Sistema de Consulta de Deudores - Velonet

Este sistema permite verificar la aptitud de instalación de nuevos clientes consultando múltiples fuentes de datos en tiempo real: **Wispro API**, **Google Sheets (Facturación)** y **Bases de Datos de Deudores Externas**.

## 🚀 Requisitos Previos

Antes de comenzar, asegúrate de tener instalado:
* Python 3.10 o superior
* Git
* Un entorno virtual (venv)

## 🛠️ Instalación y Configuración

Sigue estos pasos para ejecutar el proyecto localmente:

### 1. Clonar el repositorio
```bash
git clone [https://github.com/juanDavid0413/Consulta-deudores.git](https://github.com/juanDavid0413/Consulta-deudores.git)
cd Consulta-deudores

2. Configurar el entorno virtual
PowerShell

# Crear el entorno
python -m venv env

# Activar el entorno (Windows)
.\env\Scripts\activate

3. Instalar dependencias
Bash

pip install -r requirements.txt

4. Variables de Entorno (.env)
Crea un archivo .env en la raíz del proyecto y configura las variables (pide las credenciales al administrador)

5. Credenciales de Google Cloud
El archivo de cuenta de servicio google-service-account.json debe colocarse manualmente en la ruta: deudores/credentials/google-service-account.json (Este archivo está ignorado por Git por razones de seguridad).

🏃 Ejecución
Una vez configurado, inicia el servidor de desarrollo:

Bash

python manage.py runserver
Accede a http://127.0.0.1:8000 en tu navegador.

📁 Estructura del Proyecto
/accounts: Lógica que maneja los usuarios y los permisos.

/queries: Lógica principal de las consultas y vistas.

/Uploads: Encargada de las cargas de archivos para alimentar el sheets.

/services: Conectores para Wispro y Google Sheets API.

/templates: Plantillas HTML con diseño corporativo.

/credentials: Ubicación segura para llaves de API Google Sheets(Ignorado en Git).

/statics: archivos estaticos como imagenes e iconos. 

📧 Notificaciones
El sistema envía automáticamente un correo HTML con diseño corporativo al administrador cuando un trámite es Denegado.