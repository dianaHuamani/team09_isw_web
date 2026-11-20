from flask import Flask

from app.config import Config
from app.database import db


def create_app(config_class=Config):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config_class)
    db.init_app(app)

    from app import models  # noqa: F401
    from app.routes import bp

    app.register_blueprint(bp)
    return app
