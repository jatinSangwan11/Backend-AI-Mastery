from order import InventoryService, OrderRecord, UserOrder, place_order



def test_place_order_returns_order_result_when_stock_is_available():
    inventory = {"iphone": 5}
    inventory_service = InventoryService(inventory)

    result = place_order([UserOrder("iphone", 3)], inventory_service)

    assert result == OrderRecord(True, "Order placed", "order-1")
    assert inventory["iphone"] == 2


def test_place_order_returns_failure_when_stock_is_not_available():
    inventory = {"iphone": 5}
    inventory_service = InventoryService(inventory)

    result = place_order([UserOrder("iphone", 7)], inventory_service)

    assert result == OrderRecord(False, "Only 5 units available", None)
    assert inventory["iphone"] == 5


def test_place_order_returns_failure_when_product_does_not_exist():
    inventory = {"iphone": 5}
    inventory_service = InventoryService(inventory)

    result = place_order([UserOrder("airpods", 1)], inventory_service)

    assert result == OrderRecord(False, "Product not found", None)
    assert inventory == {"iphone": 5}


def test_place_order_reduces_inventory_for_multiple_items_when_all_are_available():
    inventory = {"iphone": 5, "macbook": 3}
    inventory_service = InventoryService(inventory)

    result = place_order(
        [
            UserOrder("iphone", 2),
            UserOrder("macbook", 1),
        ],
        inventory_service,
    )

    assert result == OrderRecord(True, "Order placed", "order-1")
    assert inventory == {"iphone": 3, "macbook": 2}


def test_place_order_does_not_reduce_any_inventory_when_one_item_is_unavailable():
    inventory = {"iphone": 5, "macbook": 3}
    inventory_service = InventoryService(inventory)

    result = place_order(
        [
            UserOrder("iphone", 2),
            UserOrder("macbook", 4),
        ],
        inventory_service,
    )

    assert result == OrderRecord(False, "Only 3 units available", None)
    assert inventory == {"iphone": 5, "macbook": 3}


def test_place_order_does_not_reduce_any_inventory_when_one_item_does_not_exist():
    inventory = {"iphone": 5, "macbook": 3}
    inventory_service = InventoryService(inventory)

    result = place_order(
        [
            UserOrder("iphone", 2),
            UserOrder("airpods", 1),
        ],
        inventory_service,
    )

    assert result == OrderRecord(False, "Product not found", None)
    assert inventory == {"iphone": 5, "macbook": 3}
