from flask import Blueprint, jsonify, request
from app.services.firebase_service import get_firestore_client

data_bp = Blueprint('data', __name__)
db = get_firestore_client()

@data_bp.route('/data-ancine/<string:collection_name>', methods=['GET'])
def get_collection(collection_name):
    """
    Endpoint genérico para buscar dados de qualquer coleção com paginação.
    Query params:
    - page: número da página (padrão: 1)
    - limit: itens por página (padrão: 10, máximo: 100)
    - Outros params: filtros (ex: ?UF=SP&year=2023)
    """
    try:
        # Parâmetros de paginação
        page = int(request.args.get('page', 1))
        limit = min(int(request.args.get('limit', 10)), 100)  # Máximo 100 itens
        
        if page < 1:
            return jsonify({'error': 'Page deve ser maior que 0'}), 400
        if limit < 1:
            return jsonify({'error': 'Limit deve ser maior que 0'}), 400
        
        query = db.collection(collection_name)
        
        # Adiciona filtros via query params (exceto page e limit)
        filter_params = {k: v for k, v in request.args.items() 
                        if k not in ['page', 'limit']}
        
        for key, value in filter_params.items():
            query = query.where(key, '==', value)
        
        # Aplica ordenação para paginação consistente
        query = query.order_by('__name__')
        
        # Calcula offset
        offset = (page - 1) * limit
        
        # Aplica paginação
        query = query.offset(offset).limit(limit)
        
        docs = query.stream()
        data = [doc.to_dict() for doc in docs]
        
        # Conta total de documentos (para metadados de paginação)
        total_query = db.collection(collection_name)
        for key, value in filter_params.items():
            total_query = total_query.where(key, '==', value)
        
        total_docs = len(list(total_query.stream()))
        total_pages = (total_docs + limit - 1) // limit  # Ceiling division
        
        response = {
            'data': data,
            'pagination': {
                'current_page': page,
                'per_page': limit,
                'total_items': total_docs,
                'total_pages': total_pages,
                'has_next': page < total_pages,
                'has_prev': page > 1
            }
        }
        
        return jsonify(response)
    except ValueError as e:
        return jsonify({'error': 'Parâmetros de paginação inválidos'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500