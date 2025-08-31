import unittest
from src.service import ItemStore

class TestItemStoreCRUD(unittest.TestCase):
    def setUp(self):
        self.store = ItemStore()

    def test_create_item_increments_id(self):
        a = self.store.create_item("Pens", 10)
        b = self.store.create_item("Notebooks", 5)
        self.assertEqual(a.id, 1)
        self.assertEqual(b.id, 2)

    def test_get_item_found_and_not_found(self):
        created = self.store.create_item("A4 Papers", 500)
        fetched = self.store.get_item(created.id)
        self.assertIsNotNone(fetched)
        self.assertEqual(fetched.name, "A4 Papers")
        self.assertIsNone(self.store.get_item(999)) 

    def test_list_items(self):
        self.store.create_item("Pens", 10)
        self.store.create_item("Notebooks", 5)
        items = self.store.list_items()
        self.assertEqual(len(items), 2)
        ids = sorted(i.id for i in items)
        self.assertEqual(ids, [1, 2])

    def test_update_name_only(self):
        created = self.store.create_item("Pen", 1)
        updated = self.store.update_item(created.id, name="Blue Pen")
        self.assertIsNotNone(updated)
        self.assertEqual(updated.name, "Blue Pen")
        self.assertEqual(updated.quantity, 1)

    def test_update_quantity_only(self):
        created = self.store.create_item("Notebook", 2)
        updated = self.store.update_item(created.id, quantity=10)
        self.assertIsNotNone(updated)
        self.assertEqual(updated.name, "Notebook")
        self.assertEqual(updated.quantity, 10)

    def test_update_nonexistent_returns_none(self):
        self.assertIsNone(self.store.update_item(123, name="X"))

    def test_delete_item(self):
        created = self.store.create_item("Ruler", 3)
        self.assertTrue(self.store.delete_item(created.id))
        self.assertFalse(self.store.delete_item(created.id)) 
        self.assertIsNone(self.store.get_item(created.id))

if __name__ == "__main__":
    unittest.main()
