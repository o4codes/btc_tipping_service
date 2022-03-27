from decouple import config

class BitnobBase:
    def __init__(self):
        self.base_url = "https://staging-api.flowertop.xyz"
        self.secret_key = config("BITNOB_SECRET_KEY")
        self.headers = {
            "Authorization": f"Bearer {self.secret_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }