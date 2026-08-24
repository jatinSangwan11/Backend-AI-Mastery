from dataclasses import dataclass


@dataclass
class OrderRecord:
    success: bool
    message: str
    order_id: str | None


@dataclass
class InventoryResult:
    success: bool
    message: str


@dataclass
class UserOrder:
    product_name: str
    quantity: int

    def __post_init__(self) -> None:
        if self.quantity <= 0:
            raise ValueError("User order quantity should be greater than 0")


@dataclass
class InventoryProduct:
    product_name: str
    quantity: int
    sku: str
    category: str | None = None

    def __post_init__(self) -> None:
        if self.quantity < 0:
            raise ValueError("Inventory quantity cannot be negative")


class InventoryService:
    def __init__(self, inventory: dict[str, InventoryProduct]) -> None:
        self.inventory = inventory

    def reduce_stock_for_order(self, order_list: list[UserOrder]) -> InventoryResult:
        inventory_copy = self.inventory.copy()

        for item in order_list:
            if item.product_name not in inventory_copy:
                return InventoryResult(False, "Product not found")

            inventory_product = inventory_copy[item.product_name]

            if inventory_product.quantity < item.quantity:
                return InventoryResult(False, f"Only {inventory_product.quantity} units available")

            inventory_copy[item.product_name] = InventoryProduct(
                product_name=inventory_product.product_name,
                quantity=inventory_product.quantity - item.quantity,
                sku=inventory_product.sku,
                category=inventory_product.category,
            )

        self.inventory.clear()
        self.inventory.update(inventory_copy)

        return InventoryResult(True, "Stock reduced")


class OrderService:
    def __init__(self, inventory_service: InventoryService) -> None:
        self.inventory_service = inventory_service

    def place_order(self, order_list: list[UserOrder]) -> OrderRecord:
        inventory_result = self.inventory_service.reduce_stock_for_order(order_list)

        if not inventory_result.success:
            return OrderRecord(False, inventory_result.message, None)

        return OrderRecord(True, "Order placed", "order-1")
