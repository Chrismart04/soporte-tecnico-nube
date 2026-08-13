# Servicio de Soporte Tecnico en la Nube
# Recibe el reporte de un usuario, valida los datos y se lo manda por correo
# al administrador usando la API de Resend.
# No usa base de datos: los datos solo sirven para validar y enviar el correo.

import re
from datetime import datetime
from zoneinfo import ZoneInfo

import requests
import streamlit as st


# Opciones del formulario
SIN_SELECCION = "-- Selecciona una opción --"

TIPOS_PROBLEMA = [
    "Acceso o contraseña",
    "Fallo de hardware",
    "Fallo de software",
    "Red o internet",
    "Correo electrónico",
    "Instalación o actualización",
    "Otro",
]

PRIORIDADES = ["Baja", "Media", "Alta", "Crítica"]

# Sirve para revisar que el correo tenga el formato algo@algo.com
PATRON_CORREO = re.compile(r"^[^@\s]+@[^@\s]+\.[a-zA-Z]{2,}$")

MIN_DESCRIPCION = 20
MAX_DESCRIPCION = 1000

ZONA_HORARIA = ZoneInfo("America/Tegucigalpa")

URL_API_RESEND = "https://api.resend.com/emails"


def validar_formulario(nombre, correo, tipo, prioridad, descripcion):
    # Devuelve una lista con los errores. Si viene vacía, se puede enviar.
    errores = []

    # Quitamos los espacios de sobra para no aceptar campos con solo espacios
    nombre = nombre.strip()
    correo = correo.strip()
    descripcion = descripcion.strip()

    if nombre == "":
        errores.append("El nombre es obligatorio.")

    if correo == "":
        errores.append("El correo electrónico es obligatorio.")
    elif not PATRON_CORREO.match(correo):
        errores.append("El correo no tiene un formato válido (ejemplo: usuario@dominio.com).")

    if tipo == SIN_SELECCION:
        errores.append("Debes seleccionar el tipo de problema.")

    if prioridad == SIN_SELECCION:
        errores.append("Debes seleccionar el nivel de prioridad.")

    if descripcion == "":
        errores.append("La descripción del problema es obligatoria.")
    elif len(descripcion) < MIN_DESCRIPCION:
        errores.append(
            "La descripción es muy corta: escribe al menos "
            f"{MIN_DESCRIPCION} caracteres."
        )

    return errores


def obtener_credenciales():
    # Las credenciales se leen de los Secrets, nunca se escriben en el código
    try:
        return st.secrets["correo"]
    except Exception:
        return None


def armar_mensaje(datos):
    # Texto que va dentro del correo
    return (
        "NUEVO REPORTE DE SOPORTE TÉCNICO\n"
        "==================================\n\n"
        f"Nombre del usuario : {datos['nombre']}\n"
        f"Correo electrónico : {datos['correo']}\n"
        f"Tipo de problema   : {datos['tipo']}\n"
        f"Nivel de prioridad : {datos['prioridad']}\n"
        f"Fecha del reporte  : {datos['fecha']}\n\n"
        "DESCRIPCIÓN DEL PROBLEMA:\n"
        f"{datos['descripcion']}\n\n"
        "==================================\n"
        "Correo enviado automáticamente por la aplicación\n"
        "de Soporte Técnico en la Nube.\n"
    )


def enviar_correo(datos):
    # Devuelve (True, "") si se envió y (False, error) si algo falló
    credenciales = obtener_credenciales()

    if credenciales is None:
        return False, "El servicio de correo no está configurado. Avisa al administrador."

    contenido = {
        "from": credenciales["remitente"],
        "to": [credenciales["correo_admin"]],
        "reply_to": datos["correo"],  # para que el admin le pueda responder al usuario
        "subject": f"[Soporte {datos['prioridad']}] {datos['tipo']} - {datos['nombre']}",
        "text": armar_mensaje(datos),
    }

    encabezados = {"Authorization": "Bearer " + credenciales["api_key"]}

    try:
        respuesta = requests.post(
            URL_API_RESEND, json=contenido, headers=encabezados, timeout=20
        )
    except Exception as error:
        return False, f"No hay conexión con el servicio de correo: {error}"

    if respuesta.status_code == 200:
        return True, ""

    if respuesta.status_code == 401:
        return False, "La clave del servicio de correo no es válida. Avisa al administrador."

    if respuesta.status_code == 429:
        return False, "Se alcanzó el límite de correos por ahora. Intenta de nuevo en un minuto."

    return False, f"No se pudo enviar el correo (error {respuesta.status_code})."


st.set_page_config(page_title="Soporte Técnico en la Nube", page_icon="🛠️")

st.sidebar.title("¿Cómo funciona?")
st.sidebar.write(
    """
    1. Completas el formulario.
    2. La aplicación valida la información.
    3. Se envía el correo al administrador.
    4. El administrador recibe tu reporte.
    5. Ves el mensaje de confirmación.
    """
)
st.sidebar.info("Esta aplicación no guarda los reportes en ninguna base de datos.")

st.title("🛠️ Servicio de Soporte Técnico en la Nube")
st.write("Sistema para **reportar problemas de soporte técnico**. "
         "Completa el formulario y tu reporte llegará al administrador.")
st.caption("Todos los campos marcados con * son obligatorios.")

with st.form("formulario_reporte"):
    nombre = st.text_input("Nombre del usuario *", placeholder="Juan Pérez")
    correo = st.text_input("Correo electrónico *", placeholder="usuario@dominio.com")
    tipo = st.selectbox("Tipo de problema *", [SIN_SELECCION] + TIPOS_PROBLEMA)
    prioridad = st.selectbox("Nivel de prioridad *", [SIN_SELECCION] + PRIORIDADES)
    descripcion = st.text_area(
        "Descripción detallada del problema *",
        height=150,
        max_chars=MAX_DESCRIPCION,
        placeholder="Explica qué pasó, desde cuándo y qué equipo o programa está fallando.",
    )

    boton_enviar = st.form_submit_button("Enviar reporte", type="primary")

if boton_enviar:

    errores = validar_formulario(nombre, correo, tipo, prioridad, descripcion)

    if errores:
        # Si hay errores se muestran y el correo no se envía
        st.error("No se pudo enviar el reporte. Corrige lo siguiente:")
        for error in errores:
            st.warning(error)
    else:
        datos = {
            "nombre": nombre.strip(),
            "correo": correo.strip(),
            "tipo": tipo,
            "prioridad": prioridad,
            "descripcion": descripcion.strip(),
            "fecha": datetime.now(ZONA_HORARIA).strftime("%d/%m/%Y %H:%M"),
        }

        with st.spinner("Enviando el reporte al administrador..."):
            enviado, mensaje_error = enviar_correo(datos)

        if enviado:
            st.success(
                "¡Reporte enviado correctamente! "
                "Su reporte ha sido enviado al administrador."
            )
            st.subheader("Resumen del reporte")
            st.write(f"**Nombre:** {datos['nombre']}")
            st.write(f"**Correo:** {datos['correo']}")
            st.write(f"**Tipo de problema:** {datos['tipo']}")
            st.write(f"**Prioridad:** {datos['prioridad']}")
            st.write(f"**Fecha:** {datos['fecha']}")
            st.write(f"**Descripción:** {datos['descripcion']}")
        else:
            st.error(mensaje_error)
