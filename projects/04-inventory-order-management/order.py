from dataclasses import dataclass


@dataclass
class OrderRecord:
    success: bool
    message: str
    order_id: str

@dataclass
class UserOrder:
    product_name: str
    quantity: int

def place_order(order_list: list[UserOrder], inventory: dict) -> OrderRecord:

    inventory_copy = inventory.copy()

    for item in order_list:
        if item.product_name not in inventory_copy:
            return OrderRecord(False, "Product not found", None)

        if inventory_copy[item.product_name] < item.quantity:
            return OrderRecord(False, f"Only {inventory_copy[item.product_name]} units available", None)

        inventory_copy[item.product_name]-= item.quantity

    inventory.clear()
    inventory.update(inventory_copy)

    return OrderRecord(True, "Order placed", "order-1")
