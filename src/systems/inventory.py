class Inventory:
    SEED_PRICE = 3
    CROP_PRICE = 5

    def __init__(self):
        self.coins = 20
        self.seeds = 5
        self.crops = 0

    def buy_seeds(self, quantity=1):
        cost = quantity * self.SEED_PRICE
        if self.coins >= cost:
            self.coins -= cost
            self.seeds += quantity
            return True
        return False

    def sell_crops(self, quantity=1):
        if quantity <= 0 or self.crops < quantity:
            return False
        self.crops -= quantity
        self.coins += quantity * self.CROP_PRICE
        return True

    def use_seed(self):
        if self.seeds > 0:
            self.seeds -= 1
            return True
        return False

    def add_crop(self, quantity=1):
        self.crops += quantity
