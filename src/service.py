from dataclasses import dataclass
from typing import Dict, Optional, List

@dataclass
class Item:
    id: int
    name: str
    quantity: int

class ItemStore:
    """Tiny in-memory CRUD store. Perfect for unit tests."""
    def __init__(self) -> None:
        self._items: Dict[int, Item] = {}
        self._next_id: int = 1

    def create_item(self, name: str, quantity: int) -> Item:
        item = Item(id=self._next_id, name=name, quantity=quantity)
        self._items[item.id] = item
        self._next_id += 1
        return item

    def get_item(self, item_id: int) -> Optional[Item]:
        return self._items.get(item_id)

    def list_items(self) -> List[Item]:
        return list(self._items.values())

    def update_item(self, item_id: int, name: Optional[str] = None, quantity: Optional[int] = None) -> Optional[Item]:
        item = self._items.get(item_id)
        if not item:
            return None
        if name is not None:
            item.name = name
        if quantity is not None:
            item.quantity = quantity
        return item

    def delete_item(self, item_id: int) -> bool:
        return self._items.pop(item_id, None) is not None
