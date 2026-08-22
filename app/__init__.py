from flask import Flask
from app.models import db
from config import Config

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)

    from app.auth import auth_bp
    app.register_blueprint(auth_bp)

    @app.route('/health')
    def health():
        return {'status': 'ok'}

    return app
