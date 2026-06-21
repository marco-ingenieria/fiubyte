from flask import Blueprint, jsonify, request
import json
from flask_jwt_extended import jwt_required, get_jwt_identity
from services.asistencias import (enviar_mails_asistencia, listar_asistencias, crear_asistencia,obtener_porcentaje_asistencia_alumno)
from utils import (construir_error)

asistencias_bp = Blueprint('asistencias', __name__)

@asistencias_bp.route('/<int:clase_id>', methods=['GET'])
def get_asistencias(clase_id):
    base_url = request.base_url
    limit = request.args.get('limit', type=int)
    offset = request.args.get('offset', type=int)

    if limit is None or limit < 0:
        limit = 10

    if offset is None or offset < 0:
        offset = 0

    asistencias = listar_asistencias(limit, offset, base_url, clase_id)
    return asistencias
'''
@asistencias_bp.route('/mail/<int:clase_id>', methods=['GET', 'POST'])
def get_mail_asistencia(clase_id):
    id_curso = None
    if request.method == 'POST':
        body = request.get_json(silent=True)
        if not body or 'id_curso' not in body:
            return construir_error(400, 'Falta id_curso para el curso')
        try:
            id_curso = int(body.get('id_curso'))
            if id_curso <= 0:
                return construir_error(400, 'id_curso inválido')
        except (ValueError, TypeError):
            return construir_error(400, 'id_curso inválido')
    else:
        id_curso = request.args.get('id_curso', type=int)

    return enviar_mails_asistencia(clase_id, id_curso)
'''

@asistencias_bp.route('/mail/<int:clase_id>', methods=['POST'])
@jwt_required()
def get_mail_asistencia(clase_id):
    id_curso = None
    body = request.get_json(silent=True)
    if not body or 'id_curso' not in body:
        return construir_error(400, 'Falta id_curso para el curso')
    try:
        id_curso = int(body.get('id_curso'))
        if id_curso <= 0:
            return construir_error(400, 'id_curso inválido')
    except (ValueError, TypeError):
        return construir_error(400, 'id_curso inválido')

    return enviar_mails_asistencia(clase_id, id_curso)

@asistencias_bp.route('/mail/<int:clase_id>', methods=['GET'])
def get_mail_asistencia(clase_id):
    id_curso = None
    
    id_curso = request.args.get('id_curso', type=int)

    return enviar_mails_asistencia(clase_id, id_curso)

@asistencias_bp.route('/registro/<int:clase_id>', methods=['GET'])
def get_registrar_asistencia(clase_id):
    padron = request.args.get('padron', type=int)

    if padron is None:
        return construir_error(400, "Falta padrón")

    return crear_asistencia(clase_id, padron)

@asistencias_bp.route('/alumno/<int:padron>/porcentaje', methods=['GET'])
def get_porcentaje_alumno(padron):
    return obtener_porcentaje_asistencia_alumno(padron)