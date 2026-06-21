from flask import Blueprint, jsonify, request
import json
from flask_jwt_extended import jwt_required, get_jwt_identity
from services.alumnos import (listar_alumnos, listar_alumno_curso, buscar_alumno, crear_alumno, actualizar_alumno, 
                              eliminar_alumno, eliminar_alumno_permanente, crear_alumnos_csv, listar_alumnos_pdf)
from utils import (construir_error)

alumnos_bp = Blueprint('alumnos', __name__)

@alumnos_bp.route('/', methods=['GET'])
def get_alumnos():
    base_url = request.base_url
    limit = request.args.get('limit', type=int)
    offset = request.args.get('offset', type=int)

    if limit is None or limit < 0:
        limit = 10

    if offset is None or offset < 0:
        offset = 0

    alumnos = listar_alumnos(limit, offset, base_url)

    return alumnos

@alumnos_bp.route('/<int:id>', methods=['GET'])
def get_alumno(id):
    alumno = buscar_alumno(id)

    return jsonify(alumno)

@alumnos_bp.route('/pdf', methods=['GET'])
def get_alumnos_pdf():
    padron      = request.args.get('padron') is not None
    nombre      = request.args.get('nombre') is not None
    apellido    = request.args.get('apellido') is not None
    email       = request.args.get('email') is not None
    id_curso    = request.args.get('id_curso') is not None
    aprobo      = request.args.get('aprobo') is not None
    abandono    = request.args.get('abandono') is not None
    
    if not padron and not nombre and not apellido and not email:
        return construir_error(400, "Datos vacíos")

    pdf = listar_alumnos_pdf(padron, nombre, apellido, email, id_curso, aprobo, abandono)
    
    return pdf


@alumnos_bp.route('/csv', methods=['POST'])
@jwt_required()
def post_alumnos_csv():
    listado_alumnos = request.files.get('alumnos')
    if not listado_alumnos:
        return construir_error(400, "Falta archivo")
    if not listado_alumnos.filename.endswith(".csv"):
        return construir_error(400, "El listado debe ser un archivo .csv")
    
    return crear_alumnos_csv(listado_alumnos)

@alumnos_bp.route('/', methods=['POST'])
@jwt_required()
def post_alumno():
    body = request.get_json()

    padron      = body.get('padron')
    nombre      = body.get('nombre')
    apellido    = body.get('apellido')
    email       = body.get('email')
    id_curso       = body.get('id_curso')
    #abandono y aprobo son 0 por default, no entran en POST

    if len(body) == 0:
        return construir_error(400, "Datos vacíos")
    if not padron or not nombre or not apellido or not email or not id_curso:
        return construir_error(400, "Faltan campos obligatorios")
    
    alumno = crear_alumno(body)
    return alumno

@alumnos_bp.route('/<int:id>', methods=['PATCH'])
@jwt_required()
def patch_alumno(id):
    body = request.get_json()

    if len(body) == 0:
        return construir_error(400, "Datos vacíos")
    
    alumno = actualizar_alumno(body, id)
    return alumno

@alumnos_bp.route('/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_alumno_virtual(id):
    return eliminar_alumno(id)

@alumnos_bp.route('/perma/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_alumno(id):
    return eliminar_alumno_permanente(id)

@alumnos_bp.route('/curso/<int:id_curso>', methods=['GET'])
def get_alumnos_curso(id_curso):
    base_url = request.base_url
    limit = request.args.get('limit', type=int)
    offset = request.args.get('offset', type=int)
    if limit is None or limit < 0:
        limit = 10
    if offset is None or offset < 0:
        offset = 0
    return listar_alumno_curso(limit, offset, base_url, id_curso)
