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
        from models import Category, Product # type: ignore  "import here so SQLAlchemy sees the model"
        db.create_all()

    from routes.root import root_bp
    from routes.product_routes import products_bp
    from routes.category_routes import category_bp
    from routes.auth_routes import auth_bp
    from routes.cart_routes import cart_bp
    from routes.order_routes import orders_bp
    app.register_blueprint(root_bp)
    app.register_blueprint(products_bp)
    app.register_blueprint(category_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(cart_bp)
    app.register_blueprint(orders_bp)

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5000, debug=True)