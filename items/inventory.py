import pygame

class Inventory:
    def __init__(self, game, capacity):
        self.game = game
        self.capacity = capacity
        self.items = {}

    def add_item(self, item_id, quantity):
        if item_id in self.items:
            self.items[item_id] += quantity
        else:
            self.items[item_id] = quantity
        print(f"Added {quantity} {item_id} to inventory. Current inventory: {self.items}")

    def remove_item(self, item_id, quantity):
        if item_id in self.items:
            if self.items[item_id] > quantity:
                self.items[item_id] -= quantity
            else:
                del self.items[item_id]
            print(f"Removed {quantity} {item_id} from inventory. Current inventory: {self.items}")
        else:
            print(f"Cannot remove {item_id}: Item not in inventory.")

    def get_item_quantity(self, item_id):
        if item_id in self.items:
            return self.items[item_id]
        else:
            return 0

    def is_full(self):
        total_items = sum(self.items.values())
        return total_items >= self.capacity