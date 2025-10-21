"""
Endpoints para filmagem estrangeira
"""
from flask_cors import CORS
# ... (outros imports)
from flask import Blueprint, jsonify, request

# from app.services.obra_service import FilmagemService  <-- LINHA INCORRETA
from app.services.producao_service import filmagem_service_instance as FilmagemService # <-- LINHA CORRETA

producao_bp = Blueprint('producao_bp', __name__)

# O resto do seu arquivo...
# ...
CORS(producao_bp)

@producao_bp.route('/filmagem-estrangeira', methods=['GET'])
def get_filmagem_estrangeira():
    """Endpoint para buscar filmagens estrangeiras."""
    try:
        # Parâmetros de paginação
        limit = min(int(request.args.get('limit', 10)), 100)
        last_id = request.args.get('last_id')
        
        # Filtros dinâmicos
        filters = {k: v for k, v in request.args.items() 
                  if k not in ['limit', 'last_id']}
        
        # Busca dados usando o service
        result = FilmagemService.get_filmagens_with_pagination(
            limit=limit,
            last_id=last_id,
            filters=filters if filters else None
        )
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': f"Erro ao buscar filmagens estrangeiras: {e}"}), 500

@producao_bp.route('/filmagem-estrangeira/pais/<string:pais_origem>', methods=['GET'])
def get_filmagem_by_pais(pais_origem):
    """Endpoint para buscar filmagens por país de origem."""
    try:
        limit = min(int(request.args.get('limit', 10)), 100)
        
        result = FilmagemService.get_filmagens_by_pais(pais_origem, limit)
        
        return jsonify({
            'data': result,
            'total': len(result),
            'pais_origem': pais_origem
        })
        
    except Exception as e:
        return jsonify({'error': f"Erro ao buscar filmagens por país: {e}"}), 500

@producao_bp.route('/filmagem-estrangeira/stats', methods=['GET'])
def get_filmagem_stats():
    """Endpoint para estatísticas de filmagem estrangeira."""
    try:
        # Este endpoint pode ser expandido para incluir estatísticas mais complexas
        # Por enquanto, retorna uma estrutura básica
        return jsonify({
            'message': 'Endpoint de estatísticas - implementar conforme necessário',
            'available_filters': [
                'pais_origem',
                'uf_filmagem',
                'municipio_filmagem',
                'tipo_producao',
                'genero',
                'situacao'
            ]
        })
        
    except Exception as e:
        return jsonify({'error': f"Erro ao buscar estatísticas: {e}"}), 500