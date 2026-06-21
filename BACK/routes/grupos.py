from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from services.grupos import (listar_grupos, obtener_grupo, crear_grupo,
                             asignar_alumnos_a_grupo, actualizar_grupo,
                             obtener_alumnos, eliminar_grupo, asignar_tp,
                             eliminar_alumno,obtener_grupos_de_un_alumno,
                             listar_grupos_pdf)
from utils import construir_error
import json
from services.historial import registrar

grupos_bp = Blueprint('grupos', __name__)

@grupos_bp.route("/", methods=['GET'])
def get_grupos():

    base_url = request.base_url
    limit = request.args.get('limit', type=int)
    offset = request.args.get('offset', type=int)

    if limit is None or limit < 0:
        limit = 10

    if offset is None or offset < 0:
        offset = 0

    return listar_grupos(base_url, limit, offset)

@grupos_bp.route("/alumnos/<int:id>", methods=['GET'])
def get_alumnos(id):
    if id <= 0:
        return construir_error(400, "id_grupo debe ser un número entero positivo")
    
    return obtener_alumnos(id)

@grupos_bp.route("/<int:id>", methods=['GET'])
def get_grupo(id):
    
    if id <= 0:
        return construir_error(400, "id_grupo debe ser un número entero positivo")
    
    return obtener_grupo(id)

@grupos_bp.route('/pdf', methods=['GET'])
def get_grupos_pdf():
    pdf = listar_grupos_pdf()

    return pdf


@grupos_bp.route("/", methods=['POST'])
@jwt_required()
@registrar("Creado un grupo")
def post_grupo():
    data=request.get_json()
    nombre = data.get('nombre')
    id_curso = data.get('id_curso')
    if not nombre:
        return construir_error(400, "Ingresar nombre")
    if not id_curso:
        return construir_error(400, "Ingresar curso")
    
    return crear_grupo(nombre, id_curso)


####post_asignar_alumnos####
def validar_json_asignar_alumnos(data):
    
    if not data:
        return False, "El cuerpo de la request no puede estar vacío" 
    
    id_grupo = data.get("id_grupo")
    padrones = data.get("padrones_alumnos")
     
    if not isinstance(padrones, list) or len(padrones) == 0:
        return False, "padrones_alumnos debe ser una lista no vacía"
    
    if not isinstance(id_grupo, int) or id_grupo <= 0:
        return False, "id_grupo debe ser un número entero positivo"
    
    padrones_invalidos = 0
    for p in padrones:
        padron = p.get("padron")
        if not isinstance(padron, int) or padron <= 0: padrones_invalidos+=1
            
    if padrones_invalidos:
        return False, f"Los padrones deben ser enteros positivos. Hay {padrones_invalidos} padrones invalidos"
    return True, "Datos validos"


@grupos_bp.route("/asignar-alumnos/", methods=['POST'])
@jwt_required()
@registrar("Asignado alumno a un grupo")
def post_asignar_alumnos():

    data=request.get_json()
    
    request_es_valido, mensaje = validar_json_asignar_alumnos(data)

    if request_es_valido:
        return asignar_alumnos_a_grupo(data.get("id_grupo"),
                                       data.get("padrones_alumnos"))
    else:
        return construir_error(400, mensaje)
    

@grupos_bp.route("/<int:id>", methods=['PATCH'])
@jwt_required()
@registrar("Actualizado un grupo")
def patch_grupo(id):

    if id <= 0:
        return construir_error(400, "id_grupo debe ser un número entero positivo")

    data=request.get_json()
    nombre_grupo = data.get("nombre_grupo")

    if not isinstance(nombre_grupo, str):
        return construir_error(400, "nombre_grupo debe ser un string")
    
    return actualizar_grupo(id, nombre_grupo)

    

@grupos_bp.route("/<int:id>", methods=['DELETE'])
@jwt_required()
@registrar("Desactivado un grupo")
def delete_grupo(id):
    if id <= 0:
        return construir_error(400, "id_grupo debe ser un número entero positivo")
    
    return eliminar_grupo(id)



@grupos_bp.route("/tp", methods=['POST'])
@jwt_required()
@registrar("Asignado TP a un grupo")
def post_tp():

    data=request.get_json()
    id_grupo = data.get('id_grupo')
    id_tp = data.get('id_tp')
    
    if not isinstance(id_grupo, int) or id_grupo <= 0:
        return construir_error(400, "id_grupo debe ser un número entero positivo"
    )
    if not isinstance(id_tp, int) or id_tp <= 0:
        return construir_error(400, "id_tp debe ser un número entero positivo")
    

    return asignar_tp(id_grupo, id_tp)



@grupos_bp.route("/alumnos", methods=['DELETE'])
@jwt_required()
@registrar("Eliminado un grupo")
def delete_alumno():

    data=request.get_json()
    id_grupo = data.get('id_grupo')
    padron_alumno = data.get('padron_alumno')
    
    if not isinstance(id_grupo, int) or id_grupo <= 0:
        return construir_error(400, "id_grupo debe ser un número entero positivo"
    )
    if not isinstance(padron_alumno, int) or padron_alumno <= 0:
        return construir_error(400, "padron_alumno debe ser un número entero positivo")
    

    return eliminar_alumno(id_grupo, padron_alumno)

# Agregá 'obtener_grupos_de_un_alumno' en el 'from services.grupos import ...' arriba de todo

@grupos_bp.route("/del-alumno/<int:padron>", methods=['GET'])
def get_grupos_del_alumno(padron):
    if padron <= 0:
        return construir_error(400, "El padrón debe ser un número entero positivo")
    
    return obtener_grupos_de_un_alumno(padron)
