# 🛠️ TechHelp IA - Plataforma SaaS de Soporte Técnico con Inteligencia Artificial

TechHelp IA es una aplicación web SaaS completa diseñada para resolver incidencias informáticas, diagnósticos de sistemas (Windows, macOS, Linux, Redes y Cloud), optimización de rendimiento y ciberseguridad mediante un asistente de Inteligencia Artificial especializado de Nivel 3.

---

## 🌟 Características Principales

- 🔐 **Autenticación y Seguridad:** Registro, inicio de sesión, sesiones seguras mediante Flask-Login y cifrado PBKDF2/SHA-256.
- 🤖 **Chat de Soporte IA Especializado:**
  - Diseñado con un System Prompt de Ingeniero Senior de Nivel 3.
  - Compatible con **Google Gemini API** y **OpenAI API**.
  - **Motor de Diagnóstico Local Inteligente:** Si no configuras claves de API, la aplicación responde automáticamente con guías técnicas detalladas paso a paso para BSOD (pantallas azules), caídas de DNS, cola de impresión bloqueada, discos saturados al 100%, scripts de Linux, etc.
- 🗂️ **Historial de Conversaciones:** Creación de múltiples casos/incidencias, guardado en SQLite y títulos auto-generados a partir del síntoma.
- 💳 **Sistema de Suscripción con Stripe:**
  - Plan Gratuito (5 consultas diarias con contador dinámico).
  - Plan Pro (19€/mes con consultas ilimitadas 24/7).
  - Stripe Checkout Session, Customer Portal para cancelaciones y Webhook handler para sincronización en tiempo real.
  - Botón de alternancia rápida "Modo Demo" para probar el plan Pro localmente sin tarjeta de crédito.
- 🛡️ **Panel de Administración Completo (`/admin`):**
  - Métricas en tiempo real: Usuarios registrados, suscriptores Pro activos, MRR mensual estimado y volumen de tickets.
  - Gestión de usuarios: buscador, asignación/revocación de plan PRO manual, privilegios de administrador y eliminación.
  - Visor y auditoría de incidencias técnicas en directo.
- 📱 **Diseño Moderno y Responsive:**
  - Creado con **Tailwind CSS**, soporte para modo oscuro nativo, Markdown enriquecido (`marked.js`), resaltado de sintaxis para comandos de terminal (`highlight.js`) y botón de un clic para copiar comandos.
- 🚀 **Listo para Producción:** Preparado para desplegarse en **Render** (con Gunicorn y `render.yaml`) o en **Vercel** (con `vercel.json`).

---

## 📁 Estructura del Proyecto

```text
techhelp-ia/
├── app.py                  # Fábrica de la aplicación Flask y configuración global
├── wsgi.py                 # Punto de entrada WSGI para Gunicorn / Render / Vercel
├── config.py               # Gestión centralizada de variables de entorno y settings
├── models.py               # Modelos SQLAlchemy: User, Conversation, Message
├── init_db.py              # Script auxiliar para inicializar la base de datos
├── requirements.txt        # Dependencias de Python
├── Procfile                # Comando de arranque para Render / Heroku
├── render.yaml             # Blueprint de infraestructura como código para Render
├── vercel.json             # Configuración Serverless para Vercel
├── .env.example            # Plantilla con todas las variables de entorno
├── .gitignore              # Archivos ignorados por Git
│
├── routes/                 # Blueprints modulares
│   ├── main.py             # Landing page, términos y privacidad
│   ├── auth.py             # Registro, login, logout y perfil
│   ├── chat.py             # Vistas de chat y endpoints REST API
│   ├── billing.py          # Checkout de Stripe, webhooks y portal de clientes
│   └── admin.py            # Dashboard administrativo y auditoría de tickets
│
├── services/               # Servicios desacoplados de negocio
│   ├── ai_service.py       # Asistente de IA (Gemini / OpenAI / Fallback local)
│   └── stripe_service.py   # Integración con Stripe Checkout y Webhooks
│
├── static/
│   ├── css/style.css       # Estilos personalizados, animaciones y Markdown
│   └── js/chat.js          # Controlador dinámico de chat en tiempo real
│
└── templates/              # Plantillas HTML con Jinja2 y Tailwind CSS
    ├── base.html           # Layout global con Navbar y notificaciones flash
    ├── index.html          # Landing page SaaS
    ├── terms.html          # Términos de servicio
    ├── privacy.html        # Política de privacidad
    ├── auth/               # Login, Registro y Perfil
    ├── chat/               # Consola interactiva de soporte
    ├── billing/            # Precios, éxito y cancelación de Stripe
    ├── admin/              # Panel administrativo y tablas de usuarios/tickets
    └── errors/             # Páginas 404, 403 y 500
```

---

## 💻 Instalación y Ejecución Local

### 1. Clonar el repositorio y navegar a la carpeta
```bash
cd techhelp-ia
```

### 2. Crear y activar entorno virtual de Python
En Windows:
```powershell
python -m venv venv
venv\Scripts\activate
```

En macOS / Linux:
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Instalar las dependencias
```bash
pip install -r requirements.txt
```

### 4. Configurar variables de entorno
Copia el archivo `.env.example` como `.env`:
```bash
cp .env.example .env
```
*(En Windows PowerShell: `copy .env.example .env`)*

Abre el archivo `.env` y configura tus claves si deseas usar proveedores externos. Si las dejas vacías, la aplicación funcionará de forma local automáticamente.

### 5. Iniciar la aplicación
```bash
python app.py
```
Abre tu navegador en: **`http://localhost:5000`**

---

## 🔑 Credenciales del Administrador por Defecto

Al arrancar por primera vez, la aplicación genera automáticamente la base de datos `techhelp.db` y crea el usuario administrador:

- **Correo:** `admin@techhelp.ia`
- **Contraseña:** `Admin123456!`
- **Panel de administración:** `http://localhost:5000/admin`

*(En la pantalla de login dispones de un botón rápido "Rellenar Administrador Demo" para probarlo con un solo clic).*

---

## 💳 Configuración de Stripe

1. Regístrate en [Stripe](https://dashboard.stripe.com/) y activa el **Modo de Prueba** (Test Mode).
2. Ve a **Desarrolladores > Claves de API** y copia:
   - `STRIPE_SECRET_KEY` (`sk_test_...`)
   - `STRIPE_PUBLISHABLE_KEY` (`pk_test_...`)
3. En **Catálogo de Productos**, crea un producto recurrente mensual llamado *"TechHelp Pro"* con un precio de **19€/mes**. Copia el **ID del precio** (ej: `price_1xxxxxx`) en `STRIPE_PRICE_ID_PRO`.
4. Para recibir webhooks en local, puedes usar el CLI de Stripe:
   ```bash
   stripe listen --forward-to localhost:5000/webhook/stripe
   ```
   Copia el secreto generado (`whsec_...`) en `STRIPE_WEBHOOK_SECRET`.

> 💡 **Nota de Desarrollo:** Si no tienes cuenta de Stripe o estás evaluando el código, puedes probar todas las funciones Pro desde `/pricing` pulsando el botón **"[Modo Demo] Alternar Pro sin tarjeta"**.

---

## 🧠 Configuración de la IA

Puedes elegir entre:
- **Google Gemini:** Obtén una clave gratuita en [Google AI Studio](https://aistudio.google.com/) y colócala en `GEMINI_API_KEY`.
- **OpenAI:** Coloca tu clave en `OPENAI_API_KEY` y define `AI_PROVIDER=openai`.
- **Modo Offline / Local:** Si no defines ninguna clave, se activa automáticamente el motor heurístico de diagnóstico para que puedas probar la aplicación sin costes ni dependencias externas.

---

## 🚀 Guía de Despliegue en Producción

### Opción A: Despliegue en Render (Recomendado)

Render es la opción más sencilla para aplicaciones Flask con Python y Gunicorn:

1. Sube tu código a un repositorio de **GitHub** o **GitLab**.
2. Inicia sesión en [Render Dashboard](https://dashboard.render.com/).
3. Haz clic en **New + > Web Service**.
4. Conecta tu repositorio de GitHub.
5. Configura los siguientes parámetros:
   - **Name:** `techhelp-ia`
   - **Region:** Selecciona la más cercana (ej: Frankfurt o Oregon).
   - **Runtime:** `Python 3`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn wsgi:app --workers 2 --timeout 120`
   - **Instance Type:** `Free`
6. En la sección **Environment Variables**, añade:
   - `SECRET_KEY`: Genera una cadena aleatoria segura.
   - `FLASK_ENV`: `production`
   - `BASE_URL`: La URL pública que te asigne Render (ej: `https://techhelp-ia.onrender.com`).
   - `STRIPE_SECRET_KEY`, `STRIPE_PUBLISHABLE_KEY`, `STRIPE_PRICE_ID_PRO` y `STRIPE_WEBHOOK_SECRET`.
   - `GEMINI_API_KEY` o `OPENAI_API_KEY`.
   - *(Opcional para persistencia a gran escala)*: Si deseas usar PostgreSQL en lugar de SQLite, crea una base de datos PostgreSQL gratuita en Render y añade `DATABASE_URL`.
7. Haz clic en **Create Web Service**. ¡Render compilará e iniciará tu aplicación en unos minutos!
8. Configura el Webhook en el Dashboard de Stripe apuntando a: `https://tu-app.onrender.com/webhook/stripe`.

---

### Opción B: Despliegue en Vercel

El repositorio incluye el archivo `vercel.json` configurado para ejecutar Flask como Serverless Function:

1. Instala el CLI de Vercel (opcional):
   ```bash
   npm install -g vercel
   ```
2. Desde la raíz del proyecto ejecuta:
   ```bash
   vercel
   ```
3. O bien, conecta tu repositorio desde la web [Vercel Dashboard](https://vercel.com/):
   - Importa el repositorio de GitHub.
   - En **Environment Variables**, añade las variables descritas en `.env.example`.
   - Haz clic en **Deploy**.

> ⚠️ *Nota sobre SQLite en Vercel:* Las funciones serverless de Vercel son de sólo lectura en su sistema de archivos efímero. Para producción permanente en Vercel, se recomienda conectar una base de datos PostgreSQL externa (por ejemplo en Neon.tech, Supabase o Render PostgreSQL) configurando la variable `DATABASE_URL`.

---

## 🛡️ Seguridad y Mantenimiento

- **Generar SECRET_KEY segura:**
  ```python
  import secrets
  print(secrets.token_hex(32))
  ```
- **Copias de seguridad de la base de datos:** El archivo `techhelp.db` contiene todas las tablas, usuarios y transcripciones de soporte. Puedes respaldarlo con una simple copia del archivo.

---

Desarrollado con ❤️ para resolver incidencias de TI rápidamente con IA.
