from flask import Flask

def create_app():
    app = Flask(__name__)
    
    # TODO: Conectar com configurações futuras
    # app.config.from_object('app.config.settings')
    
    from .api.v1.data import data_bp
    
    app.register_blueprint(data_bp, url_prefix='/api/v1')
    
    return app