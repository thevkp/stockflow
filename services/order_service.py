from extensions import db
from models import Cart, CartItem, Order, OrderItem, Product # type: ignore

class InsufficientStockError(Exception):
    pass

def place_order(user_id):
    cart = db.session.execute(
        db.select(Cart).where(Cart.user_id == user_id)
    ).scalar_one_or_none()

    if cart is None or not cart.items:
        raise ValueError("Cart is empty")

    try:
        for item in cart.items:
            if item.product.stock_quantity < item.quantity:
                raise InsufficientStockError(
                    f"Not enough stock for {item.product.name}"
                )

        total = sum(item.product.price * item.quantity for item in cart.items)
        order = Order(user_id=user_id, total_amount=total, status="confirmed")
        db.session.add(order)

        for item in cart.items:
            order_item = OrderItem(
                order=order,
                product_id=item.product_id,
                quantity=item.quantity,
                price_at_purchase=item.product.price,
            )
            db.session.add(order_item)
            item.product.stock_quantity -= item.quantity

        for item in cart.items:
            db.session.delete(item)

        db.session.commit()
        return order

    except Exception:
        db.session.rollback()
        raise