# app/api/v1/endpoints_filmagem.py

from flask import Blueprint, jsonify, request
from app.services import filmagem_service

filmagem_bp = Blueprint('filmagem_bp', __name__)

@filmagem_bp.route('/pesquisa', methods=['GET'])
def get_filmagens():
    """
    Busca detalhada de Filmagens Estrangeiras
    ---
    tags:
      - Produção
    summary: Busca dados completos de filmagens estrangeiras no Brasil.
    description: >
      Retorna uma lista paginada de filmagens estrangeiras realizadas em território brasileiro.
      Inclui informações detalhadas sobre país de origem, locações, tipo de produção e status,
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
          enum: ['Finalizada', 'Em Produção', 'Pré-produção', 'Cancelada']
          example: 'Finalizada'
        description: Filtra por status da produção.
      - in: query
        name: ano_filmagem
        schema:
          type: integer
          example: 2023
        description: Filtra por ano da filmagem.
    responses:
      200:
        description: Lista paginada de filmagens estrangeiras com dados completos.
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
                      endereco_filmagem:
                        type: string
                        description: Endereço específico da filmagem
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
                      data_inicio:
                        type: string
                        format: date
                        description: Data de início da filmagem
                      data_fim:
                        type: string
                        format: date
                        description: Data de término da filmagem
                      orcamento_estimado:
                        type: number
                        format: decimal
                        description: Orçamento estimado da produção
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
        data, pagination = filmagem_service.get_filmagens_estrangeiras(params)
        
        return jsonify({ 'data': data, 'pagination': pagination })

    except Exception as e:
        print(f"Erro em /pesquisa (filmagem): {e}") 
        return jsonify({'error': f"Ocorreu um erro interno: {e}"}), 500