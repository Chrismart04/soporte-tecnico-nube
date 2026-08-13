# Servicio de Soporte Técnico en la Nube

Aplicación web donde un usuario reporta un problema técnico por medio de un
formulario. La aplicación revisa que los datos estén correctos y envía
automáticamente un correo al administrador con el reporte.

La aplicación no usa base de datos y no guarda los reportes en ningún archivo.
Los datos solo se usan para validar el formulario y enviar el correo.

## Integrantes del equipo

| Nombre completo | Número de cuenta |
|---|---|
| (completar) | (completar) |
| (completar) | (completar) |
| (completar) | (completar) |

## Cómo funciona

El usuario entra a la aplicación desde su navegador y llena el formulario con su
nombre, su correo, el tipo de problema, el nivel de prioridad (Baja, Media, Alta
o Crítica) y la descripción del problema. Al presionar el botón "Enviar reporte"
la aplicación revisa que:

- todos los campos obligatorios estén llenos,
- el correo tenga un formato válido,
- se haya seleccionado el tipo de problema,
- se haya seleccionado la prioridad,
- la descripción tenga al menos 20 caracteres.

Si algo está mal, los errores se muestran en pantalla y el correo no se envía.
Si todo está bien, la aplicación arma el reporte y lo manda al correo del
administrador, que lo recibe con el nombre, correo, tipo de problema, prioridad,
fecha y descripción. Al final el usuario ve el mensaje "¡Reporte enviado
correctamente! Su reporte ha sido enviado al administrador." junto con un resumen
de lo que envió.

## Tecnologías utilizadas

- Python 3
- Streamlit, para la interfaz web
- La API de Resend, que es el servicio que entrega el correo
- La librería requests, para consumir esa API
- La librería re, para validar el formato del correo
- Streamlit Secrets, para guardar las credenciales de forma segura
- Streamlit Community Cloud, para publicar la aplicación

## Archivos del proyecto

- `app.py`: la aplicación completa (formulario, validaciones y envío del correo).
- `requirements.txt`: las librerías que necesita el proyecto.
- `.streamlit/config.toml`: el tema visual de la aplicación.
- `.streamlit/secrets.toml.example`: plantilla de credenciales, sin datos reales.
- `evidencias/`: capturas de pantalla del funcionamiento.
- `documentacion/enlace_aplicacion.txt`: enlaces de la aplicación y del repositorio.

## Cómo ejecutarlo

En la computadora se instalan las librerías y se corre la aplicación:

```
pip install -r requirements.txt
streamlit run app.py
```

La aplicación abre en el navegador en http://localhost:8501

Para que el envío del correo funcione hay que crear el archivo de credenciales,
copiando la plantilla y llenando los valores reales:

```
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
```

Ahí van tres datos: la clave de la API de Resend, el correo del administrador que
recibe los reportes y la dirección desde la que sale el correo.

## Sobre el servicio de correo

Se usó Resend porque tiene un plan gratuito de 100 correos al día y una API
sencilla, sin necesidad de comprar un dominio ni de configurar contraseñas de
aplicación.

Como la cuenta no tiene un dominio propio verificado, Resend obliga a enviar
desde la dirección onboarding@resend.dev y solo permite enviar al correo con el
que se creó la cuenta. Esto no afecta al proyecto, porque la aplicación siempre
envía al mismo destinatario: el administrador. Por eso la cuenta se creó con el
correo del administrador.

## Cómo se publicó en la nube

El proyecto se subió a GitHub y se publicó en Streamlit Community Cloud, en
share.streamlit.io, seleccionando el repositorio y el archivo `app.py`. Las
credenciales se cargaron desde la opción Settings → Secrets de la misma página, y
la aplicación se probó desde otro navegador para comprobar que funciona.

## Manejo seguro de las credenciales

La clave de la API no está escrita en el código. La aplicación la lee con
`st.secrets["correo"]`, que es el mecanismo de Secrets de Streamlit.

En la computadora esa clave se guarda en el archivo `.streamlit/secrets.toml`,
que está incluido en el `.gitignore`, así que nunca se sube a GitHub. En la nube
se carga desde Settings → Secrets de Streamlit Community Cloud. En el repositorio
solo quedó `secrets.toml.example`, que es una plantilla sin datos reales.

La clave viaja en el encabezado de la petición HTTPS y no aparece en ninguna de
las capturas de pantalla de las evidencias.
