from flask import jsonify
from datetime import datetime


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
    
