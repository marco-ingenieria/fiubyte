def construir_error(code: str, message: str, description: str, level: str = 'error') -> dict:
    return {
        'errors': [{
            'code': code,
            'message': message,
            'level': level,
            'description': description
        }]
    }

def construir_paginacion(listado):
    codigo_HTTP = 200 if len(listado) > 0 else 204
    
