from flask import Flask
from app.models import db
from config import Config

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)

    from app.auth import auth_bp
    app.register_blueprint(auth_bp)

    from app.routes.hints import hints_bp
    app.register_blueprint(hints_bp)

    from app.routes.challenges import challenges_bp
    app.register_blueprint(challenges_bp)

    @app.route('/health')
    def health():
        return {'status': 'ok'}

    return app
