import yaml

class Config:
    _instance = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            with open("config.yaml", "r") as f:
                cls._instance = yaml.safe_load(f)
        return cls._instance

# Accessing config
config = Config.get_instance()
