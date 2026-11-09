import json
import logging
import requests
from config import Config

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """Eres TechHelp IA, un Ingeniero Senior de Soporte Técnico Informático, Redes y Ciberseguridad (Nivel 3) con más de 15 años de experiencia.
Tu misión es resolver cualquier incidencia tecnológica reportada por el usuario con rigor técnico, empatía y extrema claridad.

Directrices de respuesta:
1. DIAGNÓSTICO: Explica brevemente la causa más probable del problema.
2. PASO A PASO: Enumera los pasos exactos para solucionarlo de menor a mayor complejidad.
3. COMANDOS PRECISOS: Si se requieren comandos de terminal (PowerShell, CMD, Bash, macOS Terminal), ponlos siempre en bloques de código con sintaxis resaltada y explica qué hace cada comando.
4. PREVENCIÓN: Ofrece una recomendación técnica para evitar que el fallo vuelva a ocurrir.
5. FORMATO: Usa Markdown impecable (negritas, listas, bloques de código, tablas si aplica). Sé directo y profesional.
"""

def generate_local_fallback(prompt: str) -> str:
    """Motor de diagnóstico inteligente local cuando no hay API Keys configuradas."""
    p = prompt.lower()
    
    if any(k in p for k in ["pantalla azul", "bsod", "cuelgue", "pantallazo", "dump"]):
        return """### 🛠️ Diagnóstico: Error de Pantalla Azul (BSOD / Stop Error)

Las pantallas azules suelen deberse a fallos en controladores recientes, corrupción de archivos del sistema o sectores defectuosos en RAM/Disco.

#### Pasos de Solución Recomendados:

**1. Reparar la imagen de Windows y archivos de sistema**
Abre **PowerShell como Administrador** (clic derecho en Menú Inicio > *Terminal / PowerShell como Administrador*) y ejecuta en orden:
```powershell
# 1. Comprobar y reparar la imagen del sistema
DISM /Online /Cleanup-Image /RestoreHealth

# 2. Verificar y reparar archivos corruptos de Windows
sfc /scannow
```
> *Reinicia el equipo al terminar.*

**2. Diagnóstico de Memoria RAM**
Presiona `Win + R`, escribe `mdsched.exe` y selecciona **Reiniciar ahora y comprobar si hay problemas**. Windows ejecutará una prueba exhaustiva de memoria antes del arranque.

**3. Revisar el código de error específico**
Si recuerdas el código Stop (ej: `CRITICAL_PROCESS_DIED`, `DRIVER_IRQL_NOT_LESS_OR_EQUAL`), descarga la herramienta ligera **BlueScreenView** de NirSoft para examinar los archivos minidump en `C:\\Windows\\Minidump`.

---
💡 **Consejo Preventivo:** Evita usar programas de actualización masiva de drivers; descarga siempre controladores oficiales del fabricante de tu placa base o GPU."""

    elif any(k in p for k in ["wifi", "wi-fi", "internet", "dns", "conexion", "red", "ping", "ethernet"]):
        return """### 🌐 Diagnóstico: Fallo de Conectividad de Red / DNS

Este problema suele estar provocado por caché DNS corrupta, asignación errónea de DHCP o problemas en el adaptador de red.

#### Pasos de Solución:

**1. Vaciar caché y renovar IP (Windows)**
Abre el **Símbolo del sistema (CMD) como Administrador** y ejecuta:
```cmd
ipconfig /flushdns
ipconfig /release
ipconfig /renew
netsh winsock reset
```
*(Reinicia el ordenador tras el último comando)*

**2. Probar DNS Públicos y Rápidos**
Si el router responde pero no cargan las páginas, cambia los servidores DNS en tu adaptador:
* **Cloudflare:** Primario `1.1.1.1` | Secundario `1.0.0.1`
* **Google:** Primario `8.8.8.8` | Secundario `8.8.4.4`

**3. Prueba de conectividad por terminal**
```bash
# Probar salida a internet por IP
ping 1.1.1.1

# Probar resolución de nombres DNS
nslookup google.com
```

---
💡 **Consejo:** Si usas cable de red, asegúrate de que el cable sea al menos Cat 5e o Cat 6 y que el enlace no esté negociando a 100 Mbps en vez de 1 Gbps."""

    elif any(k in p for k in ["lenta", "lento", "rendimiento", "optimizar", "cpu", "disco 100", "ram"]):
        return """### ⚡ Diagnóstico: Optimización y Cuello de Botella del Sistema

La lentitud suele derivarse de aplicaciones en segundo plano al arranque, disco mecánico (HDD) saturado al 100% o temperaturas elevadas con estrangulamiento térmico (Thermal Throttling).

#### Pasos de Solución:

**1. Desactivar programas de inicio innecesarios**
* Presiona `Ctrl + Shift + Esc` para abrir el **Administrador de Tareas**.
* Dirígete a la pestaña **Aplicaciones de inicio**.
* Deshabilita aplicaciones como Discord, Spotify, Steam o clientes de descarga que no requieras al encender.

**2. Limpiar temporales y caché del sistema**
Ejecuta en PowerShell como Administrador:
```powershell
# Eliminar archivos temporales de usuario y sistema
Remove-Item -Path "$env:TEMP\\*" -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item -Path "C:\\Windows\\Temp\\*" -Recurse -Force -ErrorAction SilentlyContinue
```

**3. Comprobar salud del Disco Duro o SSD**
Revisa el estado S.M.A.R.T con PowerShell:
```powershell
Get-PhysicalDisk | Select-Object DeviceId, FriendlyName, MediaType, OperationalStatus, HealthStatus
```

---
💡 **Consejo Profesional:** Si tu sistema operativo aún corre en un HDD mecánico antiguo, migrar a un SSD SATA o NVMe mejorará el rendimiento hasta un 400%."""

    elif any(k in p for k in ["impresora", "imprimir", "spooler", "cola"]):
        return """### 🖨️ Diagnóstico: Cola de Impresión Bloqueada (Print Spooler)

Es muy común que un trabajo de impresión corrupto bloquee el servicio `spoolsv.exe`, impidiendo enviar nuevos documentos.

#### Solución Rápida por Terminal:
Abre **CMD o PowerShell como Administrador** y corre este bloque completo:
```cmd
net stop spooler
del /Q /F /S "%systemroot%\\System32\\Spool\\Printers\\*.*"
net start spooler
```

**Pasos adicionales:**
1. Desconecta y vuelve a conectar el cable USB o reinicia la impresora si está por Wi-Fi.
2. En Windows: *Configuración > Bluetooth y dispositivos > Impresoras*, selecciona tu impresora y ejecuta el solucionador de problemas.

---
💡 **Consejo:** Para impresoras de red corporativas, fija una IP estática en el router para evitar pérdidas de enlace."""

    elif any(k in p for k in ["linux", "ubuntu", "debian", "ssh", "permisos", "chmod", "systemctl"]):
        return """### 🐧 Soporte Linux / SysAdmin

Para resolver incidencias en entornos Linux o servidores, aquí tienes las directrices clave:

#### 1. Verificación de logs en tiempo real:
```bash
# Inspeccionar errores del kernel o sistema
journalctl -xe -n 50 --no-pager
dmesg -T --level=err,warn
```

#### 2. Gestión de servicios del sistema:
```bash
# Comprobar estado de un servicio
sudo systemctl status <servicio>

# Reiniciar y recargar configuración
sudo systemctl restart <servicio>
```

#### 3. Permisos y espacio en disco:
```bash
# Revisar espacio disponible en particiones
df -hT

# Buscar qué directorio consume más espacio
sudo du -sh /* 2>/dev/null | sort -h
```

---
¿Cuál es el servicio o comando exacto que está arrojando error? Pega la traza del terminal para darte la solución directa."""

    else:
        return f"""### 👨‍💻 Análisis Técnico: TechHelp IA

He recibido tu consulta: **"{prompt}"**.

Para ofrecerte una resolución exacta, sigue estos pasos diagnósticos preliminares:

1. **Identificación de entorno:**
   * ¿Qué sistema operativo utilizas? (Windows 11/10, macOS Sonoma, Linux/Ubuntu, Android/iOS).
   * ¿Aparece algún código de error numérico o mensaje emergente literal?

2. **Acciones recomendadas inmediatas:**
   * Abre la consola de comandos de tu sistema y toma nota de cualquier anomalía reciente.
   * Si es un fallo de software, prueba a reiniciar el servicio o proceso implicado.

Si me compartes el mensaje de error textual o el contexto específico, te daré los comandos exactos y el procedimiento guiado paso a paso."""


def generate_ai_response(conversation_history: list, user_message: str) -> str:
    """
    Genera la respuesta del asistente usando Gemini, OpenAI o el motor local de respaldo.
    """
    gemini_key = Config.GEMINI_API_KEY
    openai_key = Config.OPENAI_API_KEY
    provider = Config.AI_PROVIDER

    # 1. Intento con Google Gemini API
    if gemini_key and (provider == 'gemini' or not openai_key):
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={gemini_key}"
            contents = []
            
            # System instruction simulado o contenido previo
            contents.append({
                "role": "user",
                "parts": [{"text": SYSTEM_PROMPT + "\n\nPor favor, responde a la incidencia del usuario con esta identidad."}]
            })
            contents.append({
                "role": "model",
                "parts": [{"text": "Entendido. Soy TechHelp IA, listo para resolver la incidencia técnica con diagnósticos claros y comandos precisos."}]
            })

            # Añadir historial reciente (últimos 6 mensajes)
            for msg in conversation_history[-6:]:
                role = "user" if msg.sender == "user" else "model"
                contents.append({
                    "role": role,
                    "parts": [{"text": msg.content}]
                })

            contents.append({
                "role": "user",
                "parts": [{"text": user_message}]
            })

            headers = {"Content-Type": "application/json"}
            payload = {
                "contents": contents,
                "generationConfig": {
                    "temperature": 0.4,
                    "maxOutputTokens": 1500,
                }
            }

            resp = requests.post(url, headers=headers, json=payload, timeout=20)
            if resp.status_code == 200:
                data = resp.json()
                answer = data["candidates"][0]["content"]["parts"][0]["text"]
                return answer
            else:
                logger.error(f"Gemini API error {resp.status_code}: {resp.text}")
        except Exception as e:
            logger.exception(f"Error llamando a Gemini API: {e}")

    # 2. Intento con OpenAI API
    if openai_key and (provider == 'openai' or not gemini_key):
        try:
            url = "https://api.openai.com/v1/chat/completions"
            messages = [{"role": "system", "content": SYSTEM_PROMPT}]
            for msg in conversation_history[-6:]:
                messages.append({
                    "role": "user" if msg.sender == "user" else "assistant",
                    "content": msg.content
                })
            messages.append({"role": "user", "content": user_message})

            headers = {
                "Authorization": f"Bearer {openai_key}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": "gpt-4o-mini",
                "messages": messages,
                "temperature": 0.4
            }
            resp = requests.post(url, headers=headers, json=payload, timeout=20)
            if resp.status_code == 200:
                data = resp.json()
                return data["choices"][0]["message"]["content"]
            else:
                logger.error(f"OpenAI API error {resp.status_code}: {resp.text}")
        except Exception as e:
            logger.exception(f"Error llamando a OpenAI API: {e}")

    # 3. Fallback inteligente local
    return generate_local_fallback(user_message)


def generate_conversation_title(first_message: str) -> str:
    """Genera un título corto y conciso para la conversación a partir del primer mensaje."""
    clean = first_message.strip()
    if len(clean) <= 45:
        return clean.capitalize()
    return clean[:42].capitalize() + "..."
