from flask import Blueprint, request
from services.notas import listar_notas, listar_notas_padron, listar_notas_evaluacion, crear_nota
from utils import construir_error

notas_bp = Blueprint('notas', __name__)

@notas_bp.route('/', methods=['GET'])
def get_notas():
    base_url = request.base_url
    limit = request.args.get('limit', type=int)
    offset = request.args.get('offset', type=int)
    padron = request.args.get('padron', type=int)
    id_evaluacion = request.args.get('id_evaluacion', type=int)

    if limit is None or limit < 0:
        limit = 10
    if offset is None or offset < 0:
        offset = 0

    if padron:
        return listar_notas_padron(limit, offset, padron)
    if id_evaluacion:
        return listar_notas_evaluacion(limit, offset, id_evaluacion)
    return listar_notas(limit, offset)

@notas_bp.route('/', methods=['POST'])
def post_nota():
    body = request.get_json()

    if not body or len(body) == 0:
        return construir_error(400, "Datos vacíos")

    nota = body.get('nota')
    padron = body.get('padron')
    id_evaluacion = body.get('id_evaluacion')

    if not nota or not padron or not id_evaluacion:
        return construir_error(400, "Faltan campos obligatorios")

    return crear_nota(padron, id_evaluacion, nota)