from flask import Flask
from flask_cors import CORS
from flasgger import Swagger

def create_app():
    app = Flask(__name__)
    CORS(app)
    
    # Configuração do Flasgger/Swagger
    swagger_config = {
        "headers": [],
        "specs": [
            {
                "endpoint": 'apispec',
                "route": '/apispec.json',
                "rule_filter": lambda rule: True,
                "model_filter": lambda tag: True,
            }
        ],
        "static_url_path": "/flasgger_static",
        "swagger_ui": True,
        "specs_route": "/docs/"
    }
    
    swagger_template = {
        "swagger": "2.0",
        "info": {
            "title": "API de Dados Abertos da ANCINE",
            "description": "API centralizada para acesso aos dados públicos da Agência Nacional do Cinema (ANCINE). Permite consultas detalhadas sobre salas de cinema, obras brasileiras, lançamentos comerciais e estatísticas do setor audiovisual.",
            "version": "1.0.0",
            "contact": {
                "name": "API ANCINE",
                "url": "https://genuine-flight-472304-e1.rj.r.appspot.com"
            },
            "license": {
                "name": "MIT",
                "url": "https://opensource.org/licenses/MIT"
            }
        },
        "host": "genuine-flight-472304-e1.rj.r.appspot.com",
        "basePath": "/",
        "schemes": ["https", "http"],
        "consumes": ["application/json"],
        "produces": ["application/json"],
        "tags": [
            {
                "name": "Exibição",
                "description": "Endpoints relacionados a salas de cinema, complexos e exibidores"
            },
            {
                "name": "Produção", 
                "description": "Endpoints de obras brasileiras e filmagens estrangeiras"
            },
            {
                "name": "Distribuição",
                "description": "Endpoints de lançamentos comerciais e dados de bilheteria"
            },
            {
                "name": "KPIs",
                "description": "Endpoints de estatísticas e indicadores agregados"
            },
            {
                "name": "Acesso Direto",
                "description": "Endpoints genéricos para acesso direto a tabelas"
            }
        ]
    }
    
    # Inicializa o Flasgger
    Swagger(app, config=swagger_config, template=swagger_template)
    
    # TODO: Conectar com configurações futuras
    # app.config.from_object('app.config.settings')
    
    # Registra todos os blueprints da API v1
    from .api.v1 import register_blueprints
    register_blueprints(app)
    
    # Rota de redirecionamento para a documentação
    @app.route('/')
    def home():
        return '''
        <h1>🎬 API de Dados Abertos da ANCINE</h1>
        <p>Bem-vindo à API centralizada dos dados públicos da ANCINE!</p>
        <p><strong><a href="/docs/">📖 Acessar Documentação Interativa (Swagger UI)</a></strong></p>
        <p><strong><a href="/apispec.json">📄 Especificação OpenAPI (JSON)</a></strong></p>
        <hr>
        <h3>🚀 Endpoints Principais:</h3>
        <ul>
            <li><strong>Exibição:</strong> <code>/api/v1/pesquisa-salas</code></li>
            <li><strong>Produção:</strong> <code>/api/v1/obras/pesquisa</code></li>
            <li><strong>Distribuição:</strong> <code>/api/v1/lancamentos/pesquisa</code></li>
            <li><strong>KPIs:</strong> <code>/api/v1/estatisticas/market_share</code></li>
        </ul>
        '''
    
    return app