class UserHOF:
    """
    When requesting selection with Limited,
    Full or Custom key, battle_stats selection will be populated.
    """
    def __init__(self, user, payload):
        self._user = user
        self.payload = payload

    def attacks(self):
        return {
            "v": self.get("attacks").get("value"),
            "r": self.get("attacks").get("rank")
        }

    def defense(self):
        return {
            "v": self.get("defends").get("value"),
            "r": self.get("defends").get("rank")
        }

    def hof_lvl(self):
        return {
            "v": self.get("level").get("value"),
            "r": self.get("level").get("rank")
        }

