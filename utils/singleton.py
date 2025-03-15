class Singleton(type): 
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)  # Calls `type.__call__` to create the instance
        return cls._instances[cls]