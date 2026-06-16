from flask import jsonify
from datetime import datetime
from smtplib import SMTP
import qrcode
from io import BytesIO
from email.message import EmailMessage
from constants import (credenciales_email)

def construir_error(code: int, description: str = '') -> dict:
    errores = {
        400: "Bad request",
        404: "Not found",
        500: "Internal server error"
    }
    return (jsonify({
        'errors': [{
            'code': code,
            'message': errores.get(code, "Unknown error"),
            'level': 'error',
            'description': description
        }]
    }), code)



def construir_paginacion(listado, base_url, limit, offset, total=None):
    if total is None:
        total = offset + len(listado)

    codigo_HTTP = 200 if len(listado) > 0 else 204
    ultimo_offset = ((total - 1) // limit) * limit if total > 0 else 0
    links = {
        "_first": f"{base_url}?limit={limit}&offset=0",
        "_prev":  f"{base_url}?limit={limit}&offset={max(0, offset - limit)}",
        "_next":  f"{base_url}?limit={limit}&offset={offset + limit}",
        "_last":  f"{base_url}?limit={limit}&offset={ultimo_offset}"
    }
    return (jsonify({
        "listado": listado,
        "links": links
    }), codigo_HTTP)



def existe_en_bd(cursor, tabla, campo, valor):
    cursor.execute(f"SELECT * FROM {tabla} WHERE {campo}=%s AND ELIMINADO=0", [valor])
    return cursor.fetchone() is not None
  
def validar_fecha(fecha):
    if not isinstance(fecha, str):
        return False
    for formato in ["%Y-%m-%d %H:%M:%S", "%Y-%m-%d"]:
        try:
            datetime.strptime(fecha, formato)
            return True
        except ValueError:
            continue
    return False
    


def enviar_mail(contenido, destinatario, asunto):
    user, password = credenciales_email
    with SMTP('smtp.gmail.com', 587) as smtp:
        smtp.ehlo()
        smtp.starttls()
        smtp.ehlo()

        smtp.login(user, password)

        contenido["Subject"] = asunto
        contenido["From"] = user
        contenido["To"] = destinatario
        smtp.send_message(contenido)

def enviar_mail_asistencia(link, fecha, mail_alumno):
    #Preparar el mensaje con la librería email
    msg = EmailMessage()
    msg.set_content("Este correo requiere soporte HTML.")
    msg.add_alternative(f"""
    <html>
        <body>
            <h1>Registrar asistencia a la clase de {fecha}</h1>
            <img src="cid:qr">
            <p>En caso de no poder escanear el QR, entrar <a href="{link}">aquí</a></p>
        </body>
    </html>
    """, subtype="html")
    
    #Generar el qr con librería qrcode
    qr_png = qrcode.make(link)
    buffer = BytesIO()
    qr_png.save(buffer, format="PNG")
    qr = buffer.getvalue()

    msg.get_payload()[0].add_related(qr, maintype="image", subtype="png", cid="qr")
    enviar_mail(msg, mail_alumno, "Registrar asistencia a la clase")
