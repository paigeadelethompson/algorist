from datetime import datetime

from tinydb.table import Document


class User:
    def __init__(self, payload: dict | Document):
        self.payload = payload
        if self.payload.get("snapshot") is None:
            self.payload["snapshot"] = str(datetime.now())

    def is_error(self):
        if self.payload.get("error") is not None:
            return True
        return False

    def error_message(self):
        raise NotImplementedError()

    def error_code(self):
        raise NotImplementedError()

    def id(self):
        return self.payload.get("player_id")

    def name(self):
        return self.payload.get("name")

    def u_lvl(self):
        return self.payload.get("level")

    def cur_hp(self):
        return self.payload.get(
            "life").get(
            "current")

    def max_hp(self):
        return self.payload.get(
            "life").get(
            "maximum")

    def stat_desc(self):
        return self.payload.get(
            "status").get(
            "description")

    def snapshot(self):
        return datetime(self.payload.get("snapshot"))

