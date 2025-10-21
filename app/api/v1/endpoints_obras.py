# app/api/v1/endpoints_obras.py

from flask import Blueprint, jsonify, request
from app.services import obra_service # Importa o serviço

# Cria um novo Blueprint para este domínio
obras_bp = Blueprint('obras_bp', __name__)

@obras_bp.route('/pesquisa', methods=['GET'])
def get_obras_com_joins():
    """
    Busca detalhada de Obras Brasileiras
    ---
    tags:
      - Produção
    summary: Busca obras cinematográficas brasileiras com países de co-produção.
    description: >
      Retorna uma lista paginada de obras brasileiras com certificado CPB.
      Cada obra inclui um array `paises_origem` com todos os países envolvidos na produção,
      permitindo análises de co-produções internacionais e mapeamento da produção nacional.
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
        description: O cursor da página anterior (usar o `cpb`).
      - in: query
        name: tipo_obra
        schema:
          type: string
          enum: ['Longa-metragem', 'Curta-metragem', 'Documentário', 'Animação']
          example: 'Longa-metragem'
        description: Filtra por categoria da produção.
      - in: query
        name: genero
        schema:
          type: string
          example: 'Drama'
        description: Filtra por gênero cinematográfico.
      - in: query
        name: ano_producao
        schema:
          type: integer
          example: 2023
        description: Filtra por ano de finalização da produção.
      - in: query
        name: situacao
        schema:
          type: string
          enum: ['Finalizada', 'Em Produção', 'Pré-produção']
          example: 'Finalizada'
        description: Filtra por status atual da obra.
      - in: query
        name: paises_origem.pais
        schema:
          type: string
          example: 'França'
        description: (Filtro Aninhado) Filtra por obras com co-produção de um país específico.
      - in: query
        name: paises_origem.tipo_participacao
        schema:
          type: string
          example: 'Co-produção'
        description: (Filtro Aninhado) Filtra por tipo de participação do país.
    responses:
      200:
        description: Uma lista paginada de obras brasileiras com dados de co-produção.
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
                      cpb:
                        type: string
                        description: Certificado de Produto Brasileiro
                      titulo_obra:
                        type: string
                        description: Título oficial da obra
                      tipo_obra:
                        type: string
                        description: Categoria da produção
                      genero:
                        type: string
                        description: Gênero cinematográfico
                      ano_producao:
                        type: integer
                        description: Ano de finalização
                      situacao:
                        type: string
                        description: Status atual
                      duracao_minutos:
                        type: integer
                        description: Duração em minutos
                      sinopse:
                        type: string
                        description: Resumo da obra
                      uf_producao:
                        type: string
                        description: Estado de produção
                      paises_origem:
                        type: array
                        items:
                          type: object
                          properties:
                            id:
                              type: integer
                              description: Identificador da relação
                            pais:
                              type: string
                              description: Nome do país
                            tipo_participacao:
                              type: string
                              description: Tipo de envolvimento
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
        params = request.args.to_dict()
        data, pagination = obra_service.get_obras_com_join(params)
        
        return jsonify({ 'data': data, 'pagination': pagination })

    except Exception as e:
        print(f"Erro em /pesquisa (obras): {e}") 
        return jsonify({'error': f"Ocorreu um erro interno: {e}"}), 500


@obras_bp.route('/estatisticas/por_tipo', methods=['GET'])
def get_stats_obras_por_tipo():
    """
    Distribuição de Obras por Categoria
    ---
    tags:
      - KPIs
    summary: Estatísticas da produção brasileira por tipo de obra.
    description: >
      Retorna dados agregados da produção cinematográfica brasileira agrupados por categoria.
      Inclui contagem total e duração média por tipo (longa-metragem, curta-metragem, etc.),
      permitindo análises do perfil da produção nacional.
    responses:
      200:
        description: Estatísticas de obras agrupadas por tipo.
        content:
          application/json:
            schema:
              type: array
              items:
                type: object
                properties:
                  tipo_obra:
                    type: string
                    description: Categoria da produção
                    example: 'Longa-metragem'
                  total_obras:
                    type: integer
                    description: Número total de obras do tipo
                    example: 450
                  duracao_media:
                    type: number
                    format: float
                    description: Duração média em minutos
                    example: 105.5
      500:
        description: Erro interno do servidor.
    """
    try:
        data = obra_service.get_stats_obras_por_tipo()
        return jsonify(data)

    except Exception as e:
        print(f"Erro em /estatisticas/por_tipo: {e}") 
        return jsonify({'error': f"Ocorreu um erro interno: {e}"}), 500