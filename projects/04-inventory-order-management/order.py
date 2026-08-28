from dataclasses import dataclass
from enum import Enum


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


class OrderStatus(Enum):
    PLACED = "PLACED"
    CANCELLED = "CANCELLED"


@dataclass
class InventoryChangeSet:
    products: dict[str, InventoryProduct]


class InventoryRepository:
    def __init__(self, inventory: dict[str, InventoryProduct]) -> None:
        self.inventory = inventory

    def begin_change_set(self) -> InventoryChangeSet:
        return InventoryChangeSet(self.inventory.copy())

    def get_product(self, change_set: InventoryChangeSet, product_name: str) -> InventoryProduct | None:
        return change_set.products.get(product_name)

    def save_product(self, change_set: InventoryChangeSet, product: InventoryProduct) -> None:
        change_set.products[product.product_name] = product

    def commit(self, change_set: InventoryChangeSet) -> None:
        self.inventory.clear()
        self.inventory.update(change_set.products)


class InventoryService:
    def __init__(self, inventory_repository: InventoryRepository) -> None:
        self.inventory_repository = inventory_repository

    def reduce_stock_for_order(self, order_list: list[UserOrder]) -> InventoryResult:
        change_set = self.inventory_repository.begin_change_set()

        for item in order_list:
            inventory_product = self.inventory_repository.get_product(change_set, item.product_name)

            if inventory_product is None:
                return InventoryResult(False, "Product not found")

            if inventory_product.quantity < item.quantity:
                return InventoryResult(False, f"Only {inventory_product.quantity} units available")

            self.inventory_repository.save_product(
                change_set,
                InventoryProduct(
                    product_name=inventory_product.product_name,
                    quantity=inventory_product.quantity - item.quantity,
                    sku=inventory_product.sku,
                    category=inventory_product.category,
                ),
            )

        self.inventory_repository.commit(change_set)

        return InventoryResult(True, "Stock reduced")

    def restore_stock_for_order(self, order_list: list[UserOrder]) -> InventoryResult:
        change_set = self.inventory_repository.begin_change_set()

        for item in order_list:
            inventory_product = self.inventory_repository.get_product(change_set, item.product_name)

            if inventory_product is None:
                return InventoryResult(False, "Product not found")

            self.inventory_repository.save_product(
                change_set,
                InventoryProduct(
                    product_name=inventory_product.product_name,
                    quantity=inventory_product.quantity + item.quantity,
                    sku=inventory_product.sku,
                    category=inventory_product.category,
                ),
            )

        self.inventory_repository.commit(change_set)

        return InventoryResult(True, "Stock restored")


@dataclass
class Order:
    order_id: str
    items: list[UserOrder]
    status: OrderStatus


class OrderRepositoryError(Exception):
    pass


class OrderRepository:
    def __init__(self) -> None:
        self.orders: list[Order] = []

    def next_order_id(self) -> str:
        return f"order-{len(self.orders) + 1}"

    def save(self, order: Order) -> None:
        self.orders.append(order)

    def get_order(self, order_id: str) -> Order | None:
        for order in self.orders:
            if order.order_id == order_id:
                return order

        return None


class OrderService:

    def __init__(self, inventory_service: InventoryService, order_repository: OrderRepository) -> None:
        self.inventory_service = inventory_service
        self.order_repository = order_repository

    def place_order(self, order_list: list[UserOrder]) -> OrderRecord:
        inventory_result = self.inventory_service.reduce_stock_for_order(order_list)

        if not inventory_result.success:
            return OrderRecord(False, inventory_result.message, None)

        try:
            order_id = self.order_repository.next_order_id()
            order = Order(order_id, order_list, OrderStatus.PLACED)
            self.order_repository.save(order)
        except OrderRepositoryError:
            self.inventory_service.restore_stock_for_order(order_list)
            return OrderRecord(False, "Order placement failed", None)

        return OrderRecord(True, "Order placed", order_id)

    def get_order(self, order_id: str) -> Order | None:
        return self.order_repository.get_order(order_id)

    def cancel_order(self, order_id: str) -> OrderRecord:
        order = self.get_order(order_id)

        if order is None:
            return OrderRecord(False, "Order not found", None)

        if order.status == OrderStatus.CANCELLED:
            return OrderRecord(False, "Order already cancelled", order_id)

        inventory_result = self.inventory_service.restore_stock_for_order(order.items)

        if not inventory_result.success:
            return OrderRecord(False, inventory_result.message, order_id)

        order.status = OrderStatus.CANCELLED
        return OrderRecord(True, "Order cancelled", order_id)
