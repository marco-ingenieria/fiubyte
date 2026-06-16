from flask import Blueprint, jsonify, request
import json
from services.asistencias import (enviar_mails_asistencia, listar_asistencias, crear_asistencia)
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

@asistencias_bp.route('/mail/<int:clase_id>', methods=['GET'])
def get_mail_asistencia(clase_id):
    return enviar_mails_asistencia(clase_id)

#GET para que se pueda acceder directamente desde el link del email
@asistencias_bp.route('/registro/<int:clase_id>', methods=['GET'])
def get_registrar_asistencia(clase_id):
    padron = request.args.get('padron', type=int)

    if padron is None:
        return construir_error(400, "Falta padrón")

    return crear_asistencia(clase_id, padron)