from dataclasses import dataclass

@dataclass
class OrderRecord:
    success: bool
    message: str
    order_id: str | None

@dataclass
class UserOrder:
    product_name: str
    quantity: int

class InventoryService:
    def __init__(self, inventory: dict[str, int]) -> None:
        self.inventory = inventory

    def reduce_stock_for_order(self, order_list: list[UserOrder]) -> OrderRecord:
        inventory_copy = self.inventory.copy()

        for item in order_list:
            if item.product_name not in inventory_copy:
                return OrderRecord(False, "Product not found", None)

            if inventory_copy[item.product_name] < item.quantity:
                return OrderRecord(False, f"Only {inventory_copy[item.product_name]} units available", None)

            inventory_copy[item.product_name] -= item.quantity

        self.inventory.clear()
        self.inventory.update(inventory_copy)

        return OrderRecord(True, "Order placed", "order-1")


def place_order(order_list: list[UserOrder], inventory_service: InventoryService) -> OrderRecord:
    return inventory_service.reduce_stock_for_order(order_list)
