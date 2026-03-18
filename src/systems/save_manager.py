import json
import os


class SaveManager:
    SAVE_DIR = "saves"
    SAVE_PATH = os.path.join(SAVE_DIR, "save_1.json")

    @classmethod
    def save_game(cls, play_state):
        os.makedirs(cls.SAVE_DIR, exist_ok=True)

        data = {
            "player": {
                "x": play_state.player.x,
                "y": play_state.player.y,
                "direction": play_state.player.direction
            },
            "money": play_state.money,
            "selected_slot": play_state.selected_slot,
            "inventory": play_state.inventory.to_dict(),
            "garden": play_state.garden.to_dict()
        }

        with open(cls.SAVE_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

    @classmethod
    def load_game(cls):
        if not os.path.exists(cls.SAVE_PATH):
            return None

        try:
            with open(cls.SAVE_PATH, "r", encoding="utf-8") as f:
                content = f.read().strip()

                if not content:
                    return None

                return json.loads(content)

        except (json.JSONDecodeError, OSError):
            return None