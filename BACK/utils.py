from flask import jsonify
from datetime import datetime
from smtplib import SMTP
import qrcode
from io import BytesIO
from email.message import EmailMessage
from email.utils import make_msgid
from constants import (credenciales_email)
from fpdf import FPDF

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
    qr_cid = make_msgid(domain="fiubyte.local")
    msg.set_content("Este correo requiere soporte HTML.")
    msg.add_alternative(f"""
    <html>
        <body>
            <h1>Registrar asistencia a la clase de {fecha}</h1>
            <img src="cid:{qr_cid[1:-1]}">
            <p>En caso de no poder escanear el QR, entrar <a href="{link}">aquí</a></p>
        </body>
    </html>
    """, subtype="html")
    
    #Generar el qr con librería qrcode
    qr_png = qrcode.make(link)
    buffer = BytesIO()
    qr_png.save(buffer, format="PNG")
    qr = buffer.getvalue()

    msg.get_payload()[1].add_related(qr, maintype="image", subtype="png", cid=qr_cid)
    enviar_mail(msg, mail_alumno, "Registrar asistencia a la clase")

def get_anchos_maximos(filas):
    #Se recorren todas las filas de cada columna para buscar el string más largo y aplicar un largo máximo
    #Sino las columnas quedan desfasadas
    #Máximo fijo no es viable porque puede pasarse del ancho de página o cortar un dato
    anchos_maximos = []
    for i in range(len(filas[0])):
        anchos_maximos.append(max([len(str(fila[i])) for fila in filas]))

    return anchos_maximos

def pdf_listado_alumnos(filas):
    anchos_maximos = get_anchos_maximos(filas)
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font('Courier', size=20, style='BU')
    pdf.cell(text="Listado de alumnos")
    pdf.ln(pdf.font_size * 2)

    pdf.set_font('Courier', size=11)
    for fila in filas:
        for indice, dato in enumerate(fila):
            pdf.cell(text=f"{str(dato).center(anchos_maximos[indice], ' ')}", border=1)
        pdf.ln(pdf.font_size)

    return pdf.output()

def pdf_listado_grupos(grupos):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font('Courier', size=20, style='BU')
    pdf.cell(text="Listado de grupos")
    pdf.ln(pdf.font_size * 2)

    for grupo in grupos:
        pdf.set_font('Courier', size=14, style='B')
        pdf.cell(text=f"Grupo {grupo['ID']} - {grupo['NOMBRE']} - Curso {grupo['ID_CURSO']}")
        pdf.ln(pdf.font_size)
        pdf.set_font('Courier', size=11)
        for integrante in grupo["INTEGRANTES"]:
            pdf.cell(text=f"* {integrante['NOMBRE']} {integrante['APELLIDO']} ({integrante['PADRON']})")
            pdf.ln(pdf.font_size)
        pdf.ln(pdf.font_size * 2)

    return pdf.output()