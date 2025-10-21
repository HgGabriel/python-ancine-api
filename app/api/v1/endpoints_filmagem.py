# app/api/v1/endpoints_filmagem.py

from flask import Blueprint, jsonify, request
from app.services import filmagem_service

filmagem_bp = Blueprint('filmagem_bp', __name__)

@filmagem_bp.route('/pesquisa', methods=['GET'])
def get_filmagens():
    """
    Endpoint para buscar dados de filmagens estrangeiras.
    """
    try:
        params = request.args.to_dict()
        data, pagination = filmagem_service.get_filmagens_estrangeiras(params)
        
        return jsonify({ 'data': data, 'pagination': pagination })

    except Exception as e:
        print(f"Erro em /pesquisa (filmagem): {e}") 
        return jsonify({'error': f"Ocorreu um erro interno: {e}"}), 500