class Inventory:
    def __init__(self, size=10):
        self.size = size
        self.slots = [None for _ in range(size)]

    def add_item(self, item_name, amount=1):
        for slot in self.slots:
            if slot is not None and slot["item"] == item_name:
                slot["amount"] += amount
                return True

        for i in range(self.size):
            if self.slots[i] is None:
                self.slots[i] = {
                    "item": item_name,
                    "amount": amount
                }
                return True

        return False

    def remove_item(self, item_name, amount=1):
        for i, slot in enumerate(self.slots):
            if slot is not None and slot["item"] == item_name:
                if slot["amount"] < amount:
                    return False

                slot["amount"] -= amount

                if slot["amount"] <= 0:
                    self.slots[i] = None

                return True

        return False

    def to_dict(self):
        return {
            "size": self.size,
            "slots": self.slots
        }

    def load_from_dict(self, data):
        self.size = data["size"]
        self.slots = data["slots"]

    def get_amount(self, item_name):
        total = 0
        for slot in self.slots:
            if slot is not None and slot["item"] == item_name:
                total += slot["amount"]
        return total

    def remove_all(self, item_name):
        total_removed = 0

        for i, slot in enumerate(self.slots):
            if slot is not None and slot["item"] == item_name:
                total_removed += slot["amount"]
                self.slots[i] = None

        return total_removed

    def get_slot(self, index):
        if 0 <= index < self.size:
            return self.slots[index]
        return None

    def get_selected_item(self, index):
        slot = self.get_slot(index)
        if slot is None:
            return None
        return slot["item"]

    def consume_from_slot(self, index, amount=1):
        slot = self.get_slot(index)

        if slot is None:
            return False

        if slot["amount"] < amount:
            return False

        slot["amount"] -= amount

        if slot["amount"] <= 0:
            self.slots[index] = None

        return True