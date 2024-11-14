import os
import zerorpc
from tinydb import TinyDB


class SandBoxConfigDB:
    def __init__(self):
        if os.environ.get("CONFIG_DB_PATH") is None:
            raise Exception("CONFIG_DB_PATH not set")
        self.config_db_path = os.environ.get("CONFIG_DB_PATH")
        if not os.access(self.config_db_path, os.W_OK):
            raise Exception("CONFIG_DB_PATH isn't writable")
        self.db = TinyDB("{}/config.db".format(self.config_db_path))

    def store_default_api_key(self, api_key):
        client = zerorpc.Client()
        client.connect(os.environ.get("REQUEST_PROCESSOR_BIND_HOST"))
        encrypted_api_key = client.encrypt_api_key(api_key)
        if len(self.db.table("default_api_key").all()) > 0:
            self.db.table("default_api_key").truncate()
            self.db.table("default_api_key").remove()
        self.db.table("default_api_key").insert({"value": encrypted_api_key})

    def get_default_api_key(self):
        if len(self.db.table("default_api_key").all()) <= 0:
            raise Exception("No default api key is set")
        ret = self.db.table("default_api_key").all().pop().get("value")
        return ret