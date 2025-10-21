from flask import Blueprint, jsonify, request
from app.services import lancamento_service

lancamentos_bp = Blueprint('lancamentos_bp', __name__)

@lancamentos_bp.route('/pesquisa', methods=['GET'])
def get_lancamentos():
    """
    Busca detalhada de Lançamentos Comerciais
    ---
    tags:
      - Distribuição
    summary: Busca dados de bilheteria com informações de distribuidoras e obras.
    description: >
      Retorna uma lista paginada de lançamentos comerciais com dados completos de bilheteria.
      Cada lançamento inclui informações da distribuidora responsável e, quando aplicável,
      dados da obra brasileira associada. Filmes estrangeiros terão `obras: null`.
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
        description: O cursor da página anterior (usar o `id`).
      - in: query
        name: ano_lancamento
        schema:
          type: integer
          example: 2023
        description: Filtra por ano do lançamento comercial.
      - in: query
        name: titulo_filme
        schema:
          type: string
          example: 'Homem-Aranha'
        description: Filtra por título do filme (busca parcial).
      - in: query
        name: distribuidoras.razao_social_distribuidora
        schema:
          type: string
          example: 'DISNEY'
        description: (Filtro Aninhado) Filtra por empresa distribuidora.
      - in: query
        name: distribuidoras.cnpj_distribuidora
        schema:
          type: string
          example: '98.765.432/0001-10'
        description: (Filtro Aninhado) Filtra por CNPJ da distribuidora.
      - in: query
        name: obras.cpb
        schema:
          type: string
          example: 'B2023001234'
        description: (Filtro Aninhado) Filtra por certificado CPB da obra brasileira.
      - in: query
        name: obras.tipo_obra
        schema:
          type: string
          example: 'Longa-metragem'
        description: (Filtro Aninhado) Filtra por tipo da obra brasileira.
    responses:
      200:
        description: Uma lista paginada de lançamentos com dados de bilheteria.
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
                        description: Identificador único do lançamento
                      cpb_roe:
                        type: string
                        description: CPB (brasileiro) ou ROE (estrangeiro)
                      titulo_filme:
                        type: string
                        description: Título comercial do filme
                      data_lancamento:
                        type: string
                        format: date
                        description: Data do lançamento comercial
                      ano_lancamento:
                        type: integer
                        description: Ano do lançamento
                      publico_total:
                        type: integer
                        description: Número total de espectadores
                      renda_total:
                        type: number
                        format: decimal
                        description: Receita total em reais
                      distribuidoras:
                        type: object
                        properties:
                          registro_distribuidora:
                            type: string
                            description: Identificador único da distribuidora
                          razao_social_distribuidora:
                            type: string
                            description: Nome empresarial
                          cnpj_distribuidora:
                            type: string
                            description: CNPJ ou "PESSOA FÍSICA"
                      obras:
                        type: object
                        nullable: true
                        description: Dados da obra brasileira (null para filmes estrangeiros)
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
        data, pagination = lancamento_service.get_lancamentos_com_join(params)
        
        return jsonify({ 'data': data, 'pagination': pagination })

    except Exception as e:
        print(f"Erro em /pesquisa (lancamentos): {e}") 
        return jsonify({'error': f"Ocorreu um erro interno: {e}"}), 500