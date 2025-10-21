from flask import Flask
from flask_cors import CORS

def create_app():
    app = Flask(__name__)
    CORS(app)
    
    # TODO: Conectar com configurações futuras
    # app.config.from_object('app.config.settings')
    
    # Registra todos os blueprints da API v1
    from .api.v1 import register_blueprints
    register_blueprints(app)
    
    return app