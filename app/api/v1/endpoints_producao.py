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
    """
    Busca de Filmagens Estrangeiras no Brasil
    ---
    tags:
      - Produção
    summary: Busca dados de produções estrangeiras filmadas no Brasil.
    description: >
      Retorna uma lista paginada de filmagens estrangeiras realizadas em território brasileiro.
      Inclui informações sobre país de origem, locações, tipo de produção e status,
      permitindo análises do impacto econômico e geográfico das produções internacionais.
    parameters:
      - in: query
        name: limit
        schema:
          type: integer
          default: 10
          maximum: 100
        description: Número de itens por página.
      - in: query
        name: last_id
        schema:
          type: string
        description: O cursor da página anterior.
      - in: query
        name: pais_origem
        schema:
          type: string
          example: 'Estados Unidos'
        description: Filtra por país de origem da produção.
      - in: query
        name: uf_filmagem
        schema:
          type: string
          example: 'RJ'
        description: Filtra por estado onde ocorreu a filmagem.
      - in: query
        name: municipio_filmagem
        schema:
          type: string
          example: 'Rio de Janeiro'
        description: Filtra por município da filmagem.
      - in: query
        name: tipo_producao
        schema:
          type: string
          example: 'Longa-metragem'
        description: Filtra por tipo de produção.
      - in: query
        name: genero
        schema:
          type: string
          example: 'Ação'
        description: Filtra por gênero cinematográfico.
      - in: query
        name: situacao
        schema:
          type: string
          example: 'Finalizada'
        description: Filtra por status da produção.
    responses:
      200:
        description: Lista paginada de filmagens estrangeiras.
        content:
          application/json:
            schema:
              type: object
              properties:
                data:
                  type: array
                  items:
                    type: object
                    properties:
                      id:
                        type: integer
                        description: Identificador único da filmagem
                      titulo_producao:
                        type: string
                        description: Título da produção
                      pais_origem:
                        type: string
                        description: País de origem da produção
                      uf_filmagem:
                        type: string
                        description: Estado da filmagem
                      municipio_filmagem:
                        type: string
                        description: Município da filmagem
                      tipo_producao:
                        type: string
                        description: Categoria da produção
                      genero:
                        type: string
                        description: Gênero cinematográfico
                      situacao:
                        type: string
                        description: Status da produção
                      ano_filmagem:
                        type: integer
                        description: Ano da filmagem
                pagination:
                  type: object
                  properties:
                    total_filtered_count:
                      type: integer
                    per_page:
                      type: integer
                    next_cursor:
                      type: string
                    has_next:
                      type: boolean
      500:
        description: Erro interno do servidor.
    """
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
    """
    Filmagens por País de Origem
    ---
    tags:
      - Produção
    summary: Busca filmagens estrangeiras de um país específico.
    description: >
      Retorna todas as filmagens estrangeiras realizadas no Brasil por um país específico.
      Útil para análises de parcerias cinematográficas bilaterais e impacto econômico
      por país de origem.
    parameters:
      - in: path
        name: pais_origem
        required: true
        schema:
          type: string
        description: Nome do país de origem da produção.
        example: 'Estados Unidos'
      - in: query
        name: limit
        schema:
          type: integer
          default: 10
          maximum: 100
        description: Número de itens por página.
    responses:
      200:
        description: Lista de filmagens do país especificado.
        content:
          application/json:
            schema:
              type: object
              properties:
                data:
                  type: array
                  items:
                    type: object
                    properties:
                      id:
                        type: integer
                      titulo_producao:
                        type: string
                      uf_filmagem:
                        type: string
                      municipio_filmagem:
                        type: string
                      tipo_producao:
                        type: string
                      genero:
                        type: string
                      situacao:
                        type: string
                      ano_filmagem:
                        type: integer
                total:
                  type: integer
                  description: Total de filmagens encontradas
                pais_origem:
                  type: string
                  description: País consultado
      500:
        description: Erro interno do servidor.
    """
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
    """
    Estatísticas de Filmagem Estrangeira
    ---
    tags:
      - KPIs
    summary: Estatísticas agregadas de filmagens estrangeiras no Brasil.
    description: >
      Retorna informações sobre filtros disponíveis e estrutura para futuras
      implementações de estatísticas de filmagem estrangeira. Endpoint preparado
      para expansão com métricas de impacto econômico e distribuição geográfica.
    responses:
      200:
        description: Informações sobre filtros disponíveis e estrutura do endpoint.
        content:
          application/json:
            schema:
              type: object
              properties:
                message:
                  type: string
                  description: Status do endpoint
                available_filters:
                  type: array
                  items:
                    type: string
                  description: Lista de filtros disponíveis para consultas
      500:
        description: Erro interno do servidor.
    """
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