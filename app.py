from flask import Flask
from config import Config
from extensions import db, migrate, jwt



def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    with app.app_context():
        from models import Category, Product # import here so SQLAlchemy sees the model
        db.create_all()

    from routes.root import root_bp
    from routes.product_routes import products_bp
    app.register_blueprint(root_bp)
    app.register_blueprint(products_bp)

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5000, debug=True)