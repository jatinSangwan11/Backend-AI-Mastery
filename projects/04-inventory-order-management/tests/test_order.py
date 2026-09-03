import pytest

from order import (
    InMemoryUnitOfWork,
    InventoryProduct,
    InventoryService,
    InventoryRepository,
    Order,
    OrderRecord,
    OrderRepositoryError,
    OrderService,
    OrderStatus,
    OrderRepository,
    UnitOfWorkError,
    UserOrder,
)


def test_place_order_returns_order_result_when_stock_is_available():
    inventory = {
        "iphone": InventoryProduct("iphone", 5, "IPHONE-15", "phone"),
    }
    inventory_repository = InventoryRepository(inventory)
    inventory_service = InventoryService(inventory_repository)
    order_repository = OrderRepository()
    unit_of_work = InMemoryUnitOfWork(inventory_repository, order_repository)
    order_service = OrderService(inventory_service, unit_of_work)

    result = order_service.place_order([UserOrder("iphone", 3)])

    assert result == OrderRecord(True, "Order placed", "order-1")
    assert order_repository.orders == [
        Order("order-1", [UserOrder("iphone", 3)], OrderStatus.PLACED),
    ]
    assert inventory["iphone"].quantity == 2
    assert inventory["iphone"].sku == "IPHONE-15"
    assert inventory["iphone"].category == "phone"


def test_get_order_returns_placed_order_by_order_id():
    inventory = {
        "iphone": InventoryProduct("iphone", 5, "IPHONE-15", "phone"),
    }
    inventory_repository = InventoryRepository(inventory)
    inventory_service = InventoryService(inventory_repository)
    order_repository = OrderRepository()
    unit_of_work = InMemoryUnitOfWork(inventory_repository, order_repository)
    order_service = OrderService(inventory_service, unit_of_work)

    result = order_service.place_order([UserOrder("iphone", 3)])

    assert order_service.get_order(result.order_id) == Order(
        "order-1",
        [UserOrder("iphone", 3)],
        OrderStatus.PLACED,
    )


def test_get_order_returns_none_when_order_does_not_exist():
    inventory = {
        "iphone": InventoryProduct("iphone", 5, "IPHONE-15", "phone"),
    }
    inventory_repository = InventoryRepository(inventory)
    inventory_service = InventoryService(inventory_repository)
    order_repository = OrderRepository()
    unit_of_work = InMemoryUnitOfWork(inventory_repository, order_repository)
    order_service = OrderService(inventory_service, unit_of_work)

    assert order_service.get_order("missing-order") is None


def test_cancel_order_changes_placed_order_status_to_cancelled():
    inventory = {
        "iphone": InventoryProduct("iphone", 5, "IPHONE-15", "phone"),
    }
    inventory_repository = InventoryRepository(inventory)
    inventory_service = InventoryService(inventory_repository)
    order_repository = OrderRepository()
    unit_of_work = InMemoryUnitOfWork(inventory_repository, order_repository)
    order_service = OrderService(inventory_service, unit_of_work)

    result = order_service.place_order([UserOrder("iphone", 3)])
    cancel_result = order_service.cancel_order(result.order_id)

    assert cancel_result == OrderRecord(True, "Order cancelled", "order-1")
    assert order_service.get_order("order-1") == Order(
        "order-1",
        [UserOrder("iphone", 3)],
        OrderStatus.CANCELLED,
    )
    assert inventory["iphone"].quantity == 5


def test_cancel_order_returns_failure_when_order_does_not_exist():
    inventory = {
        "iphone": InventoryProduct("iphone", 5, "IPHONE-15", "phone"),
    }
    inventory_repository = InventoryRepository(inventory)
    inventory_service = InventoryService(inventory_repository)
    order_repository = OrderRepository()
    unit_of_work = InMemoryUnitOfWork(inventory_repository, order_repository)
    order_service = OrderService(inventory_service, unit_of_work)

    assert order_service.cancel_order("missing-order") == OrderRecord(
        False,
        "Order not found",
        None,
    )


def test_cancel_order_returns_failure_when_order_is_already_cancelled():
    inventory = {
        "iphone": InventoryProduct("iphone", 5, "IPHONE-15", "phone"),
    }
    inventory_repository = InventoryRepository(inventory)
    inventory_service = InventoryService(inventory_repository)
    order_repository = OrderRepository()
    unit_of_work = InMemoryUnitOfWork(inventory_repository, order_repository)
    order_service = OrderService(inventory_service, unit_of_work)

    result = order_service.place_order([UserOrder("iphone", 3)])
    order_service.cancel_order(result.order_id)
    second_cancel_result = order_service.cancel_order(result.order_id)

    assert second_cancel_result == OrderRecord(
        False,
        "Order already cancelled",
        "order-1",
    )
    assert order_service.get_order("order-1").status == OrderStatus.CANCELLED


def test_place_order_returns_failure_when_stock_is_not_available():
    inventory = {
        "iphone": InventoryProduct("iphone", 5, "IPHONE-15", "phone"),
    }
    inventory_repository = InventoryRepository(inventory)
    inventory_service = InventoryService(inventory_repository)
    order_repository = OrderRepository()
    unit_of_work = InMemoryUnitOfWork(inventory_repository, order_repository)
    order_service = OrderService(inventory_service, unit_of_work)

    result = order_service.place_order([UserOrder("iphone", 7)])

    assert result == OrderRecord(False, "Only 5 units available", None)
    assert inventory["iphone"].quantity == 5


def test_place_order_returns_failure_when_product_does_not_exist():
    inventory = {
        "iphone": InventoryProduct("iphone", 5, "IPHONE-15", "phone"),
    }
    inventory_repository = InventoryRepository(inventory)
    inventory_service = InventoryService(inventory_repository)
    order_repository = OrderRepository()
    unit_of_work = InMemoryUnitOfWork(inventory_repository, order_repository)
    order_service = OrderService(inventory_service, unit_of_work)

    result = order_service.place_order([UserOrder("airpods", 1)])

    assert result == OrderRecord(False, "Product not found", None)
    assert inventory == {
        "iphone": InventoryProduct("iphone", 5, "IPHONE-15", "phone"),
    }


def test_place_order_restores_inventory_when_order_save_fails():
    class FailingOrderRepository(OrderRepository):
        def save(self, order: Order) -> None:
            raise OrderRepositoryError("Database failed")

    inventory = {
        "iphone": InventoryProduct("iphone", 5, "IPHONE-15", "phone"),
    }
    inventory_repository = InventoryRepository(inventory)
    inventory_service = InventoryService(inventory_repository)
    order_repository = FailingOrderRepository()
    unit_of_work = InMemoryUnitOfWork(inventory_repository, order_repository)
    order_service = OrderService(inventory_service, unit_of_work)

    result = order_service.place_order([UserOrder("iphone", 3)])

    assert result == OrderRecord(False, "Order placement failed", None)
    assert inventory == {
        "iphone": InventoryProduct("iphone", 5, "IPHONE-15", "phone"),
    }
    assert order_repository.orders == []


def test_place_order_returns_critical_failure_when_unit_of_work_rollback_fails():
    class FailingOrderRepository(OrderRepository):
        def save(self, order: Order) -> None:
            raise OrderRepositoryError("Database failed")

    class FailingUnitOfWork(InMemoryUnitOfWork):
        def rollback(self) -> None:
            raise UnitOfWorkError("Rollback failed")

    inventory = {
        "iphone": InventoryProduct("iphone", 5, "IPHONE-15", "phone"),
    }
    inventory_repository = InventoryRepository(inventory)
    inventory_service = InventoryService(inventory_repository)
    order_repository = FailingOrderRepository()
    unit_of_work = FailingUnitOfWork(inventory_repository, order_repository)
    order_service = OrderService(inventory_service, unit_of_work)

    result = order_service.place_order([UserOrder("iphone", 3)])

    assert result == OrderRecord(
        False,
        "Order placement failed and rollback failed",
        None,
    )
    assert inventory["iphone"].quantity == 2
    assert order_repository.orders == []


def test_place_order_does_not_hide_unexpected_order_save_error():
    class BrokenOrderRepository(OrderRepository):
        def save(self, order: Order) -> None:
            raise RuntimeError("Programming bug")

    inventory = {
        "iphone": InventoryProduct("iphone", 5, "IPHONE-15", "phone"),
    }
    inventory_repository = InventoryRepository(inventory)
    inventory_service = InventoryService(inventory_repository)
    order_repository = BrokenOrderRepository()
    unit_of_work = InMemoryUnitOfWork(inventory_repository, order_repository)
    order_service = OrderService(inventory_service, unit_of_work)

    with pytest.raises(RuntimeError, match="Programming bug"):
        order_service.place_order([UserOrder("iphone", 3)])
    assert inventory["iphone"].quantity == 5


def test_place_order_reduces_inventory_for_multiple_items_when_all_are_available():
    inventory = {
        "iphone": InventoryProduct("iphone", 5, "IPHONE-15", "phone"),
        "macbook": InventoryProduct("macbook", 3, "MACBOOK-PRO", "laptop"),
    }
    inventory_repository = InventoryRepository(inventory)
    inventory_service = InventoryService(inventory_repository)
    order_repository = OrderRepository()
    unit_of_work = InMemoryUnitOfWork(inventory_repository, order_repository)
    order_service = OrderService(inventory_service, unit_of_work)

    result = order_service.place_order(
        [
            UserOrder("iphone", 2),
            UserOrder("macbook", 1),
        ],
    )

    assert result == OrderRecord(True, "Order placed", "order-1")
    assert inventory == {
        "iphone": InventoryProduct("iphone", 3, "IPHONE-15", "phone"),
        "macbook": InventoryProduct("macbook", 2, "MACBOOK-PRO", "laptop"),
    }


def test_place_order_does_not_reduce_any_inventory_when_one_item_is_unavailable():
    inventory = {
        "iphone": InventoryProduct("iphone", 5, "IPHONE-15", "phone"),
        "macbook": InventoryProduct("macbook", 3, "MACBOOK-PRO", "laptop"),
    }
    inventory_repository = InventoryRepository(inventory)
    inventory_service = InventoryService(inventory_repository)
    order_repository = OrderRepository()
    unit_of_work = InMemoryUnitOfWork(inventory_repository, order_repository)
    order_service = OrderService(inventory_service, unit_of_work)

    result = order_service.place_order(
        [
            UserOrder("iphone", 2),
            UserOrder("macbook", 4),
        ],
    )

    assert result == OrderRecord(False, "Only 3 units available", None)
    assert inventory == {
        "iphone": InventoryProduct("iphone", 5, "IPHONE-15", "phone"),
        "macbook": InventoryProduct("macbook", 3, "MACBOOK-PRO", "laptop"),
    }


def test_place_order_does_not_reduce_any_inventory_when_one_item_does_not_exist():
    inventory = {
        "iphone": InventoryProduct("iphone", 5, "IPHONE-15", "phone"),
        "macbook": InventoryProduct("macbook", 3, "MACBOOK-PRO", "laptop"),
    }
    inventory_repository = InventoryRepository(inventory)
    inventory_service = InventoryService(inventory_repository)
    order_repository = OrderRepository()
    unit_of_work = InMemoryUnitOfWork(inventory_repository, order_repository)
    order_service = OrderService(inventory_service, unit_of_work)

    result = order_service.place_order(
        [
            UserOrder("iphone", 2),
            UserOrder("airpods", 1),
        ],
    )

    assert result == OrderRecord(False, "Product not found", None)
    assert inventory == {
        "iphone": InventoryProduct("iphone", 5, "IPHONE-15", "phone"),
        "macbook": InventoryProduct("macbook", 3, "MACBOOK-PRO", "laptop"),
    }


def test_inventory_product_quantity_cannot_be_negative():
    with pytest.raises(ValueError, match="Inventory quantity cannot be negative"):
        InventoryProduct("iphone", -1, "IPHONE-15", "phone")


def test_user_order_quantity_should_be_greater_than_zero():
    with pytest.raises(ValueError, match="User order quantity should be greater than 0"):
        UserOrder("iphone", -2)
