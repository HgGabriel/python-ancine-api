from flask import Blueprint, jsonify, request
from app.services import lancamento_service

lancamentos_bp = Blueprint('lancamentos_bp', __name__)

@lancamentos_bp.route('/pesquisa', methods=['GET'])
def get_lancamentos():
    """
    ENDPOINT PODEROSO (Lançamentos): Busca dados de bilheteria
    com JOINs em Distribuidoras e Obras (se for brasileiro).
    """
    try:
        params = request.args.to_dict()
        data, pagination = lancamento_service.get_lancamentos_com_join(params)
        
        return jsonify({ 'data': data, 'pagination': pagination })

    except Exception as e:
        print(f"Erro em /pesquisa (lancamentos): {e}") 
        return jsonify({'error': f"Ocorreu um erro interno: {e}"}), 500