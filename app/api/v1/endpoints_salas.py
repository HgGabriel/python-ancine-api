# app/api/v1/endpoints_salas.py

from flask import Blueprint, jsonify, request
# Importa o *serviço* que tem a lógica
from app.services import sala_service 

# Renomeia o Blueprint para ser mais específico
salas_bp = Blueprint('salas_bp', __name__)
# O CORS pode ser gerenciado globalmente no app/__init__.py

@salas_bp.route('/<string:table_name>', methods=['GET'])
def get_table_cursor(table_name):
    """
    Acesso direto a tabelas de exibição
    ---
    tags:
      - Exibição
    summary: Busca dados de salas, complexos ou exibidores sem relacionamentos.
    description: >
      Endpoint genérico para acesso direto aos dados de infraestrutura de exibição.
      Retorna dados "planos" (sem JOINs) das tabelas salas, complexos ou exibidores,
      ideal para análises que precisam apenas dos dados de uma entidade específica.
    parameters:
      - in: path
        name: table_name
        required: true
        schema:
          type: string
          enum: ['salas', 'complexos', 'exibidores']
        description: Nome da tabela de exibição a ser consultada.
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
        description: Cursor da página anterior (usar a chave primária do último item).
    responses:
      200:
        description: Lista paginada de registros da tabela de exibição solicitada.
        content:
          application/json:
            schema:
              type: object
              properties:
                data:
                  type: array
                  items:
                    type: object
                    description: Estrutura varia conforme a tabela (salas, complexos ou exibidores).
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
      400:
        description: Nome de tabela inválido.
      500:
        description: Erro interno do servidor.
    """
    try:
        # 1. Pega os parâmetros da URL
        params = request.args.to_dict()
        
        # 2. Chama o SERVIÇO para fazer o trabalho
        data, pagination = sala_service.get_generic_table_data(table_name, params)
        
        # 3. Apenas retorna a resposta
        return jsonify({ 'data': data, 'pagination': pagination })

    except ValueError as e: # Captura o erro "Nome de tabela inválido"
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        print(f"Erro em /data/{table_name}: {e}") 
        return jsonify({'error': f"Ocorreu um erro interno: {e}"}), 500
    
@salas_bp.route('/estatisticas/salas_por_uf', methods=['GET'])
def get_stats_salas_por_uf():
    """
    Distribuição de Salas por Estado
    ---
    tags:
      - KPIs
    summary: Estatísticas de infraestrutura de exibição por UF.
    description: >
      Retorna dados agregados da distribuição de salas de cinema por unidade federativa.
      Inclui contagem total de salas, poltronas e complexos por estado, permitindo
      análises de concentração geográfica da infraestrutura cinematográfica brasileira.
    responses:
      200:
        description: Estatísticas de salas agrupadas por UF.
        content:
          application/json:
            schema:
              type: array
              items:
                type: object
                properties:
                  uf_complexo:
                    type: string
                    description: Unidade federativa
                    example: 'SP'
                  total_salas:
                    type: integer
                    description: Número total de salas no estado
                    example: 1250
                  total_poltronas:
                    type: integer
                    description: Capacidade total de assentos
                    example: 180000
                  media_poltronas_por_sala:
                    type: number
                    format: float
                    description: Média de poltronas por sala
                    example: 144.5
                  total_complexos:
                    type: integer
                    description: Número de complexos cinematográficos
                    example: 85
      500:
        description: Erro interno do servidor.
    """
    if supabase is None:
        return jsonify({'error': 'Serviço Supabase não está disponível.'}), 503
        
    try:
        # 'rpc' chama a função SQL que acabamos de criar
        response = supabase.rpc('contar_salas_por_uf').execute()
        
        return jsonify(response.data)

    except Exception as e:
        print(f"Erro em /estatisticas/salas_por_uf: {e}") 
        return jsonify({'error': f"Ocorreu um erro interno: {e}"}), 500

@salas_bp.route('/pesquisa', methods=['GET'])
def get_salas_com_joins():
    """
    Busca detalhada de Salas de Cinema
    ---
    tags:
      - Exibição
    summary: Busca salas de cinema com dados aninhados de complexos e exibidores.
    description: >
      Retorna uma lista paginada de salas de cinema. Cada sala na resposta contém
      um objeto aninhado `complexos`, que por sua vez contém um objeto aninhado `exibidores`.
      Permite filtros avançados em campos das tabelas relacionadas, ideal para análises
      geográficas e de infraestrutura de exibição.
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
        description: O cursor da página anterior (usar o `registro_sala`).
      - in: query
        name: situacao_sala
        schema:
          type: string
          enum: ['Em Funcionamento', 'Fechado', 'Em Construção', 'Reformando']
          example: 'Em Funcionamento'
        description: Filtra pela situação operacional da sala.
      - in: query
        name: tipo_tela
        schema:
          type: string
          example: '2D'
        description: Filtra por tecnologia de projeção (2D, 3D, IMAX, etc.).
      - in: query
        name: tipo_som
        schema:
          type: string
          example: 'DOLBY DIGITAL'
        description: Filtra por sistema de áudio.
      - in: query
        name: complexos.uf_complexo
        schema:
          type: string
          example: 'SP'
        description: (Filtro Aninhado) Filtra por salas localizadas num estado (UF) específico.
      - in: query
        name: complexos.municipio_complexo
        schema:
          type: string
          example: 'São Paulo'
        description: (Filtro Aninhado) Filtra por salas localizadas numa cidade específica.
      - in: query
        name: complexos.exibidores.nome_grupo_exibidor
        schema:
          type: string
          example: 'CINEMARK'
        description: (Filtro Aninhado) Filtra por salas pertencentes a um grupo exibidor.
    responses:
      200:
        description: Uma lista paginada de salas com dados aninhados.
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
                      registro_sala:
                        type: string
                        description: Identificador único da sala
                      nome_sala:
                        type: string
                        description: Nome oficial da sala
                      situacao_sala:
                        type: string
                        description: Situação operacional
                      tipo_tela:
                        type: string
                        description: Tecnologia de projeção
                      tipo_som:
                        type: string
                        description: Sistema de áudio
                      poltronas:
                        type: integer
                        description: Número de assentos
                      complexos:
                        type: object
                        properties:
                          registro_complexo:
                            type: string
                            description: Identificador único do complexo
                          nome_complexo:
                            type: string
                            description: Nome do complexo/shopping
                          uf_complexo:
                            type: string
                            description: Unidade federativa
                          municipio_complexo:
                            type: string
                            description: Município
                          endereco_complexo:
                            type: string
                            description: Endereço completo
                          exibidores:
                            type: object
                            properties:
                              registro_exibidor:
                                type: string
                                description: Identificador único do exibidor
                              nome_grupo_exibidor:
                                type: string
                                description: Nome do grupo empresarial
                              cnpj_exibidor:
                                type: string
                                description: CNPJ da empresa
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
        # 1. Pega os parâmetros
        params = request.args.to_dict()
        
        # 2. Chama o SERVIÇO
        data, pagination = sala_service.get_salas_com_join(params)
        
        # 3. Retorna a resposta
        return jsonify({ 'data': data, 'pagination': pagination })

    except Exception as e:
        print(f"Erro em /pesquisa-salas: {e}") 
        return jsonify({'error': f"Ocorreu um erro interno: {e}"}), 500