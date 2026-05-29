def construir_error(code: int, description: str = '') -> dict:
    errores = {
        400: "Bad request",
        404: "Not found",
        500: "Internal server error"
    }

    return ({
        'errors': [{
            'code': code,
            'message': errores.get(code, "Unknown error"),
            'level': 'error',
            'description': description
        }]
    }, code)

def construir_paginacion(listado, base_url, limit, offset):
    codigo_HTTP = 200 if len(listado) > 0 else 204

    total = len(listado)

    ultimo_offset = ((total - 1) // limit) * limit if total > 0 else 0

    links = {
        "_first": f"{base_url}?limit={limit}&offset=0",
        "_prev":  f"{base_url}?limit={limit}&offset={max(0, offset - limit)}",
        "_next":  f"{base_url}?limit={limit}&offset={offset + limit}",
        "_last":  f"{base_url}?limit={limit}&offset={ultimo_offset}"
    }

    return ({
        "listado": listado,
        "links": links
    }, codigo_HTTP)