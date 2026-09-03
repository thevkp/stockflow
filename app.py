from flask import Flask
from config import Config
from extensions import db, migrate, jwt



def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    # app.py (add this inside create_app, after db.init_app)

    @app.cli.command("create-admin")
    def create_admin():
        """Create an admin user."""
        import getpass
        from models.user import User

        username = input("Username: ")
        password = getpass.getpass("Password: ")

        existing = db.session.execute(
            db.select(User).where(User.username == username)
        ).scalar_one_or_none()
        if existing:
            print(f"User '{username}' already exists.")
            return

        user = User(username=username, role="admin")
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        print(f"Admin '{username}' created.")   

    with app.app_context():
        from models import User, Category, Product, Cart, CartItem, Order, OrderItem # type: ignore  "import here so SQLAlchemy sees the model"
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