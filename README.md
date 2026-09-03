# stockflow
E-commerce platform using Flask

# StockFlow

A layered Inventory & Order Management REST API built with Flask, SQLAlchemy, and JWT-based authentication with role-based access control (RBAC). Built as a hands-on project to complement FastAPI experience with Flask.

## Features

- **Auth**: Registration, login, JWT access tokens, role-based access control (`admin` / `customer`)
- **Products**: Full CRUD, category association
- **Categories**: Full CRUD
- **Cart**: Add/view/remove items, automatic quantity merging for duplicate items
- **Orders**: Transactional checkout — validates stock, deducts inventory, snapshots purchase price, clears cart, all wrapped in a single atomic transaction with rollback on failure
- **Migrations**: Schema managed via Flask-Migrate (Alembic)
- **Containerized**: Dockerized with an entrypoint that runs migrations automatically on startup

## Architecture

The project follows a layered structure to separate concerns:

```
stockflow/
├── app.py              # Application factory, entry point
├── config.py            # Configuration (env-based)
├── extensions.py         # Shared extension instances (db, migrate, jwt)
├── entrypoint.sh          # Runs migrations, then starts the app (used by Docker)
│
├── models/               # SQLAlchemy models — table structure only
│   ├── user.py
│   ├── category.py
│   ├── product.py
│   ├── cart.py
│   └── order.py
│
├── services/              # Business logic layer
│   └── order_service.py    # Checkout: stock validation, order creation, transactional rollback
│
├── routes/                # Blueprints — thin, parse request & call services/models
│   ├── auth_routes.py
│   ├── product_routes.py
│   ├── category_routes.py
│   ├── cart_routes.py
│   └── order_routes.py
│
├── utils/
│   └── decorators.py       # role_required — custom RBAC decorator built on flask-jwt-extended
│
├── migrations/             # Alembic migration history
└── instance/                # SQLite database (gitignored, mounted as a Docker volume)
```

**Why this structure:** models hold table definitions only; routes stay thin and call into models or services rather than embedding business logic; the service layer handles multi-step operations (like checkout) that need to succeed or fail as a single transactional unit.

## Tech Stack

- Flask + Flask-SQLAlchemy + Flask-Migrate (Alembic)
- Flask-JWT-Extended for token issuance/verification
- bcrypt for password hashing
- SQLite (dev) — swappable to Postgres via `DATABASE_URL`
- Docker

## Running Locally

```bash
python3 -m venv myvenv
source myvenv/bin/activate
pip install -r requirements.txt

export FLASK_APP=app.py
flask db upgrade

python app.py
```

The API is available at `http://127.0.0.1:5000`.

## Running with Docker

```bash
docker build -t stockflow .
docker run -p 5000:5000 -v $(pwd)/instance:/app/instance stockflow
```

The entrypoint script runs `flask db upgrade` automatically before starting the app, so a fresh container (empty volume) will build its own schema on first run. The mounted volume persists the SQLite database across container restarts.

## Environment Variables

Create a `.env` file in the project root:

```
SECRET_KEY=<random-secret>
JWT_SECRET_KEY=<random-secret>
DATABASE_URL=sqlite:///stockflow.db
```

Generate secrets with:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

## API Endpoints

### Auth (`/api/auth`)
| Method | Endpoint    | Description            | Auth   |
| ------ | ----------- | ---------------------- | ------ |
| POST   | `/register` | Create a new user      | Public |
| POST   | `/login`    | Get a JWT access token | Public |

### Products (`/api/products`)
| Method | Endpoint | Description          | Auth   |
| ------ | -------- | -------------------- | ------ |
| GET    | ``       | List all products    | Public |
| GET    | `/<id>`  | Get a single product | Public |
| POST   | ``       | Create a product     | Admin  |
| PUT    | `/<id>`  | Update a product     | Admin  |
| DELETE | `/<id>`  | Delete a product     | Admin  |

### Categories (`/api/categories`)
| Method | Endpoint | Description           | Auth   |
| ------ | -------- | --------------------- | ------ |
| GET    | ``       | List all categories   | Public |
| GET    | `/<id>`  | Get a single category | Public |
| POST   | ``       | Create a category     | Admin  |
| PUT    | `/<id>`  | Update a category     | Admin  |
| DELETE | `/<id>`  | Delete a category     | Admin  |

### Cart (`/api/cart`)
| Method | Endpoint      | Description                  | Auth |
| ------ | ------------- | ---------------------------- | ---- |
| GET    | ``            | View current user's cart     | User |
| POST   | `/items`      | Add an item to the cart      | User |
| DELETE | `/items/<id>` | Remove an item from the cart | User |

### Orders (`/api/orders`)
| Method | Endpoint    | Description                                                                            | Auth |
| ------ | ----------- | -------------------------------------------------------------------------------------- | ---- |
| POST   | `/checkout` | Place an order from the current cart (validates stock, deducts inventory, clears cart) | User |

## Design Notes

- **Price snapshotting**: `OrderItem.price_at_purchase` is stored separately from `Product.price` so historical orders aren't affected by later price changes.
- **Transactional checkout**: `place_order()` validates stock for every cart item *before* making any changes, then performs all writes (order creation, stock deduction, cart clearing) inside a single try/except block with `db.session.rollback()` on failure — ensuring partial failures never leave inconsistent data.
- **RBAC**: A custom `role_required(role)` decorator checks the `role` claim embedded in the JWT at registration/login time, rather than relying solely on library defaults — write access to Products/Categories is restricted to `admin` users.